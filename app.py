"""Launch from the installed project with python -m streamlit run app.py."""
from dataclasses import asdict, replace
import io
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from proposal_pid.physics import Config, SPECIES, evaluate
from proposal_pid.data import compare_counts
from proposal_pid.learning import load_model, predict

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='ParticleID proposal lab',layout='wide')
st.title('ParticleID proposal lab')
st.caption('Equations (1)–(9) • numerical tests • PyTorch • future measurement comparison')
st.info('No experimental data have been supplied. Equation outputs and synthetic AI accuracy do not establish experimental validity.')
page=st.segmented_control('Workspace',['Equations','PyTorch prediction','Measurement comparison'],default='Equations',key='workspace')


@st.cache_data(max_entries=24)
def calculate(config_json):
    return evaluate(Config(**json.loads(config_json)))


@st.cache_resource(max_entries=4)
def cached_network(path,task,mtime):
    return load_model(path,task)


cfg=Config.load(ROOT/'configs/proposal.json')
if page == 'Equations':
    st.subheader('Evaluate the proposal')
    st.caption('Defaults and missing physical inputs are declared in configs/proposal.json and EQUATIONS.md.')
    with st.form('equations'):
        cols=st.columns(3)
        p=cols[0].number_input('Initial momentum (GeV/c)',min_value=.101,max_value=14.999,value=5.,key='p0')
        x=cols[1].number_input('Shared coordinate x (cm)',min_value=.001,max_value=20.,value=1.,key='x')
        n=cols[2].number_input('Refractive index (constant over wavelength)',min_value=1.,max_value=1.01,value=1.0005,step=.00001,format='%.6f',key='n')
        material=st.selectbox('Material',['Al','Pb'],key='material')
        evolution=st.selectbox('Momentum evolution',['proposal','kinematic'],key='evolution')
        q2=st.selectbox('Effective momentum-transfer convention',['printed_cm','angular_diagnostic'],key='q2')
        grouping=st.selectbox('Equation (8) grouping',['difference_over_noise','literal_slash'],key='grouping')
        submitted=st.form_submit_button('Evaluate equations',key='evaluate',type='primary')
    if submitted:
        case=replace(cfg,p0_MeV=p*1000,x_cm=x,n_values=(n,)*3,material=material,
                     evolution=evolution,q2_convention=q2,detector_grouping=grouping)
        try:
            result=calculate(json.dumps(asdict(case)))
            frame=pd.DataFrame(result['rows'])
            st.dataframe(frame[['species','W','U','R','I','P_cherenkov','D','P_conditional','P_joint','p_exit_MeV','scalar_probability_valid']],
                         hide_index=True,alt='Proposal operator factors and detection values by species')
            st.caption('P_joint includes W; P_conditional does not. A value in [0,1] is only a numerical range check, not physical validation.')
            tracks=pd.concat([pd.DataFrame({'s_cm':t['s_cm'],'momentum_GeV_c':[v/1000 for v in t['p_MeV']],'species':t['species']}) for t in result['trajectories']],ignore_index=True)
            st.line_chart(tracks,x='s_cm',y='momentum_GeV_c',color='species',alt='Momentum trajectories computed from equation nine')
            for message in dict.fromkeys(m for row in result['rows'] for m in row['warnings']):
                st.warning(message)
            st.download_button('Download equation results',json.dumps(result,indent=2),'equations.json','application/json')
        except ValueError as error:
            st.error(str(error))

elif page == 'PyTorch prediction':
    st.subheader('Use trained PyTorch models')
    folder=st.text_input('Model folder relative to this project',value='example_run',key='model_folder')
    st.caption('The shipped example_run contains trained .pt checkpoints. After retraining, select runs/demo. The old joblib model is not used.')
    mode=st.segmented_control('Model',['Particle classifier','Equation surrogate'],default='Particle classifier',key='model_mode')
    with st.form('inference'):
        if mode == 'Particle classifier':
            momentum=st.number_input('Measured downstream momentum (GeV/c)',min_value=.000001,value=5.,key='momentum')
            tof=st.number_input('Downstream time of flight (ns)',min_value=.000001,value=33.36,key='tof')
            npe=st.number_input('Cherenkov photoelectrons',min_value=0,value=12,step=1,key='npe')
        else:
            species=st.selectbox('Species',list(SPECIES),key='species')
            beam=st.number_input('Initial beam momentum (GeV/c)',min_value=.001,value=5.,key='beam')
            thickness=st.number_input('Shared coordinate (cm)',min_value=.001,value=1.,key='thickness')
            ref=st.number_input('Refractive index',min_value=1.,value=1.0005,step=.00001,format='%.6f',key='ref')
        submit=st.form_submit_button('Run PyTorch inference',key='infer',type='primary')
    if submit:
        task='classifier' if mode == 'Particle classifier' else 'surrogate'
        model_path=ROOT/folder/(task+'.pt')
        try:
            model,bundle=cached_network(str(model_path),task,model_path.stat().st_mtime_ns)
            values=[[momentum,tof,npe]] if task == 'classifier' else [[beam,thickness,ref,*[int(s == species) for s in SPECIES]]]
            output,outside=predict(model,bundle,values)
            if task == 'classifier':
                st.success('Predicted particle: '+bundle['classes'][int(output[0].argmax())])
                st.dataframe(pd.DataFrame({'Species':bundle['classes'],'Softmax score':output[0]}),hide_index=True,alt='PyTorch classifier scores by species')
                st.caption('Uncalibrated scores; balanced synthetic incident species, 10 m downstream flight path, 15% photoelectron efficiency. This does not measure proposal validity.')
            else:
                st.metric('PyTorch approximation of conditional equation value',f'{output[0]:.6g}')
                saved=Config.load(ROOT/folder/'model_config.json')
                direct=evaluate(replace(saved,p0_MeV=beam*1000,x_cm=thickness,n_values=(ref,)*3))['rows'][SPECIES.index(species)]
                st.metric('Direct numerical equation value',f"{direct['P_conditional']:.6g}")
                st.caption('The surrogate approximates its equation-generated training targets, with a 1e-12 floor. Direct evaluation is the reference; emulation agreement is not experimental evidence.')
            if bool(outside[0]):
                st.warning('At least one transformed input is outside the saved training range. This is extrapolation; do not rely on this result.')
        except Exception as error:
            st.error(f'Cannot produce a model prediction: {error}')
            st.caption('No substitute model or hardcoded prediction is used. Train with: proposal-pid run --config configs/proposal.json --output runs/demo')

else:
    st.subheader('Compare independently measured counts')
    st.markdown('Use counts for **independently identified incident particles of each species**. AI predictions must not supply their own ground-truth labels. The experiment’s trigger and calibration must match the predicted quantity.')
    st.download_button('Download empty measurement template',(ROOT/'templates/measurements.csv').read_bytes(),'measurements.csv','text/csv')
    uploaded=st.file_uploader('Measurement CSV',type=['csv'],key='measurements')
    if uploaded is not None:
        if st.button('Compare counts',key='compare'):
            try:
                result_frame=compare_counts(pd.read_csv(io.BytesIO(uploaded.getvalue())),cfg)
                st.dataframe(result_frame,hide_index=True,alt='Observed counts compared with fixed-parameter proposal predictions')
                if (result_frame.source_kind == 'synthetic').any():
                    st.warning('Synthetic rows test code consistency only. They are not independent validation.')
                st.caption('Exact binomial tests, 95% count intervals and Holm-adjusted p-values. A high p-value does not prove the equations. Systematic errors are not included.')
                st.download_button('Download comparison',result_frame.to_csv(index=False),'comparison.csv','text/csv')
            except (ValueError,KeyError) as error:
                st.error(str(error))
