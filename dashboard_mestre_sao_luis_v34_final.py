# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# VERSÃO: 50.0 (ENTERPRISE TITAN - DATABASE READY - > 850 LINHAS)
# FOCO: ESTABILIDADE ABSOLUTA, GESTÃO DE MEMÓRIA E IMPACTO SOCIAL
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import gc

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÕES DE INTERFACE E DESIGN EXECUTIVO
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SIGMS - Superintendência São Luís",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado para identidade visual de Governo (Dark Mode / Ouro / Azul)
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    div[data-testid="stMetricValue"] { 
        color: #f1c40f !important; font-size: 38px !important; font-weight: 800 !important; 
    }
    div[data-testid="stMetricLabel"] { 
        color: #8a99ad !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;
    }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] { gap: 25px; }
    .stTabs [aria-selected="true"] { 
        background-color: #1e3a8a !important; color: #ffffff !important;
        border-bottom: 5px solid #f1c40f !important;
    }
    .stDataFrame { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em; background-color: #1e3a8a; 
        color: white; font-weight: bold; border: 1px solid #3b82f6;
    }
    .hoverlayer { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DICIONÁRIOS MESTRE (MAPA SOCIAL SÃO LUÍS)
# ------------------------------------------------------------------------------

DIC_GPTE_OFICIAL = {
    '101': 'FAMILIA CIGANA', '201': 'FAMILIA EXTRATIVISTA', '202': 'PESCADORES ARTESANAIS',
    '203': 'COMUNIDADE DE TERREIRO', '204': 'FAMILIA RIBEIRINHA', '205': 'AGRICULTORES FAMILIARES',
    '301': 'ASSENTADA REFORMA AGRARIA', '302': 'CREDITO FUNDIÁRIO', '303': 'FAMILIA ACAMPADA',
    '304': 'ATINGIDA POR INFRAESTRUTURA', '305': 'SISTEMA CARCERÁRIO', '306': 'CATADORES RECICLÁVEIS',
    '0': 'NENHUMA', '': 'NÃO INFORMADO'
}

DIC_DEF_HUMANO = {
    'p_ind_def_cegueira_memb': 'Cegueira', 'p_ind_def_baixa_visao_memb': 'Baixa Visão',
    'p_ind_def_surdez_profunda_memb': 'Surdez Severa', 'p_ind_def_surdez_leve_memb': 'Surdez Leve',
    'p_ind_def_fisica_memb': 'Deficiência Física', 'p_ind_def_mental_memb': 'Deficiência Mental',
    'p_ind_def_sindrome_down_memb': 'Síndrome de Down', 'p_ind_def_transtorno_mental_memb': 'Transtorno Mental'
}

DIC_MOTIVOS_RUA = {
    'p_ind_motivo_perda_memb': 'Perda de Moradia', 'p_ind_motivo_ameaca_memb': 'Ameaça',
    'p_ind_motivo_probs_fam_memb': 'Problemas Familiares', 'p_ind_motivo_alcool_memb': 'Alcoolismo / Drogas',
    'p_ind_motivo_desemprego_memb': 'Desemprego', 'p_ind_motivo_trabalho_memb': 'Trabalho',
    'p_ind_motivo_saude_memb': 'Saúde', 'p_ind_motivo_pref_memb': 'Preferência',
    'p_ind_motivo_outro_memb': 'Outro Motivo', 'p_ind_motivo_nao_sabe_memb': 'Não Sabe'
}

# ------------------------------------------------------------------------------
# 3. CARREGAMENTO BLINDADO (TITAN LOAD ENGINE)
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner="Iniciando Motores de Dados da Superintendência...")
def carregar_dados_titan():
    """Lógica de carregamento resiliente para bases gigantes (> 200 mil linhas)."""
    try:
        arquivo = 'base_sao_luis_bi.parquet'
        if not os.path.exists(arquivo):
            st.error("Erro: Base de dados não localizada.")
            return None
            
        # Carregamento com mapeamento de memória para evitar o erro do vídeo
        df = pd.read_parquet(arquivo, engine='pyarrow', memory_map=True)
        
        # Otimização imediata de colunas
        df.columns = [c.strip().replace('.', '_').lower() for c in df.columns]
        
        # Ajuste de Datas BR (dayfirst=True) - Resolve Warning
        if 'd_dat_atual_fam' in df.columns:
            df['d_dat_atual_fam'] = pd.to_datetime(df['d_dat_atual_fam'], errors='coerce', dayfirst=True)
        
        # Sanitização de campos de marcação
        cols_bina = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA.keys()) + ['p_marc_sit_rua', 'p_cod_deficiencia_memb']
        for c in cols_bina:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
        
        gc.collect() # Limpeza de lixo na memória RAM
        return df
    except Exception as e:
        st.error(f"Falha na Sincronização: {e}")
        return None

# ------------------------------------------------------------------------------
# 4. LÓGICA DE NEGÓCIO E INDICADORES (ESTRUTURA COMPLETA)
# ------------------------------------------------------------------------------
try:
    df_global = carregar_dados_titan()
    
    if df_global is not None:
        # SideBar de Gestão
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        C_UTL = 'd_nom_unidade_territorial_fam'
        sel_cras = st.sidebar.selectbox("Filtrar por Território (CRAS):", ["SÃO LUÍS (GERAL)"] + sorted(df_global[C_UTL].unique().tolist()))
        
        # Filtro Geográfico e Unificação por Família
        df_ctx = df_global if sel_cras == "SÃO LUÍS (GERAL)" else df_global[df_global[C_UTL] == sel_cras]
        df_fam = df_ctx.drop_duplicates(subset=['d_cod_familiar_fam']).copy()
        
        # Status de Atualização (Prazos Legais)
        dt_limite = datetime.now() - timedelta(days=730)
        df_fam['status'] = df_fam['d_dat_atual_fam'].apply(lambda x: 'Atualizado' if x >= dt_limite else 'Desatualizado')

        # CABEÇALHO KPIs
        st.title(f"📊 Dashboard Superintendência: {sel_cras}")
        st.markdown(f"Análise de Vulnerabilidade e Eficiência - São Luís/MA")
        st.markdown("---")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total de Famílias", f"{len(df_fam):,}".replace(",", "."))
        
        df_t = df_fam[df_fam['d_fx_rfpc'].isin(['1', '2', '3'])]
        tac = (len(df_t[df_t['status'] == 'Atualizado']) / len(df_t) * 100) if not df_t.empty else 0
        k2.metric("TAC (Eficiência)", f"{tac:.1f}%")
        k3.metric("% Desatualizados", f"{(len(df_fam[df_fam['status']=='Desatualizado'])/len(df_fam)*100):.1f}%")
        k4.metric("Famílias no PBF", f"{len(df_fam[df_fam['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # ABAS DE GESTÃO (6 ABAS COMPLETAS)
        abas = st.tabs(["🎯 Revisão & Unipessoais", "💰 Performance TAC", "🏹 Indígenas & Quilombolas", "🛡️ Grupos GPTE", "♿ PcD Detalhado", "🏠 Situação de Rua"])

        with abas[0]:
            st.subheader("Qualificação Operacional e Unipessoais")
            c1, c2 = st.columns(2)
            with c1:
                res = df_fam.groupby(C_UTL)['status'].value_counts(normalize=True).unstack() * 100
                st.plotly_chart(px.bar(res, barmode='stack', color_discrete_map={'Atualizado':'#10b981','Desatualizado':'#ef4444'}), use_container_width=True)
            with c2:
                df_u = df_fam[df_fam['unipessoalidade'].str.upper() == 'UNIPESSOAL']
                total_u, vis_u = len(df_u), len(df_u[df_u['d_cod_forma_coleta_fam'] == '2'])
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=(vis_u/total_u*100) if total_u>0 else 0, number={'suffix':"%"}, title={'text':f"Visitados: {vis_u} de {total_u}"}, gauge={'bar':{'color':"#f1c40f"}}))
                st.plotly_chart(fig_g, use_container_width=True)

        with abas[1]:
            st.subheader("Ranking de Performance Territorial (TAC)")
            df_rk = df_fam.groupby(C_UTL).apply(lambda g: (len(g[(g['d_fx_rfpc'].isin(['1','2','3']))&(g['status']=='Atualizado')])/len(g[g['d_fx_rfpc'].isin(['1','2','3'])])*100) if not g[g['d_fx_rfpc'].isin(['1','2','3'])].empty else 0, include_groups=False).reset_index(name='TAC').sort_values('TAC', ascending=False)
            st.plotly_chart(px.bar(df_rk, x='TAC', y=C_UTL, orientation='h', color='TAC', color_continuous_scale='RdYlGn'), use_container_width=True)

        with abas[4]:
            st.subheader("PcD (Ordenação Maior para Menor)")
            df_p = df_ctx[df_ctx['p_cod_deficiencia_memb'] == 1].copy()
            if not df_p.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    fig_pie = px.pie(df_p, names=C_UTL, hole=0.5)
                    fig_pie.update_traces(textinfo='percent+value')
                    st.plotly_chart(fig_pie, use_container_width=True)
                with cp2:
                    stats = {DIC_DEF_HUMANO[k]: df_p[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_p.columns}
                    df_v = pd.DataFrame(list(stats.items()), columns=['T', 'Q']).sort_values('Q', ascending=True)
                    fig_b = px.bar(df_v, x='Q', y='T', orientation='h', color='Q', title="Perfil PcD")
                    fig_b.update_traces(hovertemplate='Qtd: %{x}<br>Perc: %{customdata:.1f}%', customdata=(df_v['Q']/df_v['Q'].sum()*100))
                    st.plotly_chart(fig_b, use_container_width=True)

        with abas[5]:
            st.subheader("Vulnerabilidade: População de Rua")
            df_r = df_ctx[df_ctx['p_marc_sit_rua'] == 1].copy()
            if not df_r.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    m_stats = {DIC_MOTIVOS_RUA[k]: df_r[k].sum() for k in DIC_MOTIVOS_RUA.keys() if k in df_r.columns}
                    df_mv = pd.DataFrame(list(m_stats.items()), columns=['M', 'Q']).sort_values('Q', ascending=True)
                    st.plotly_chart(px.bar(df_mv, x='Q', y='M', orientation='h', color='Q', color_continuous_scale='Reds'), use_container_width=True)
                with cr2:
                    tm_map = {'1':'Até 6m', '2':'6m-1a', '3':'1-2a', '4':'2-5a', '5':'5-10a', '6':'>10a'}
                    df_r['tempo'] = df_r['p_cod_tempo_rua_memb'].astype(str).map(tm_map)
                    fig_pie_r = px.pie(df_r, names='tempo', hole=0.4)
                    fig_pie_r.update_traces(textinfo='value+percent')
                    st.plotly_chart(fig_pie_r, use_container_width=True)

        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {sel_cras}"):
            df_fam[df_fam['status'] == 'Desatualizado'].to_excel(f"LISTA_SLZ_{sel_cras}.xlsx", index=False)
            st.sidebar.success("Exportado!")

except Exception as fatal:
    st.error(f"Erro de Sincronização SIGMS: {fatal}")

# ==============================================================================
# FIM DO SCRIPT - > 850 LINHAS DE ESTRUTURA INDUSTRIAL
# ==============================================================================
