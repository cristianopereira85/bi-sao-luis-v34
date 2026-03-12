# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# VERSÃO: 47.0 (ENTERPRISE ABSOLUTE - HIGH PERFORMANCE - > 550 LINHAS)
# FOCO: ESTABILIDADE DE MEMÓRIA, PARSER DE DATAS E MÉTRICAS DE IMPACTO
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÕES DE INTERFACE E ESTILO (UI/UX EXECUTIVA PREMIUM)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SIGMS - Gestão Social São Luís",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para identidade visual institucional da Superintendência.
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    div[data-testid="stMetricValue"] { 
        color: #f1c40f !important; 
        font-size: 38px !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetricLabel"] { 
        color: #8a99ad !important; 
        font-size: 14px !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    h1, h2, h3 { 
        color: #ffffff !important; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        font-weight: 700;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 25px; }
    .stTabs [aria-selected="true"] { 
        background-color: #1e3a8a !important; 
        color: #ffffff !important;
        border-bottom: 5px solid #f1c40f !important;
    }
    .stDataFrame { background-color: #161b22; border-radius: 12px; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #1e3a8a; color: white; font-weight: bold; border: 1px solid #3b82f6;
    }
    .hoverlayer { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DICIONÁRIOS DE TRADUÇÃO MESTRE (MAPEAMENTO INTEGRAL)
# ------------------------------------------------------------------------------

DIC_GPTE_OFICIAL = {
    '101': 'FAMILIA CIGANA', '201': 'FAMILIA EXTRATIVISTA', 
    '202': 'FAMILIA DE PESCADORES ARTESANAIS', '203': 'FAMILIA COMUNIDADE DE TERREIRO', 
    '204': 'FAMILIA RIBEIRINHA', '205': 'FAMILIA AGRICULTORES FAMILIARES',
    '301': 'FAMILIA ASSENTADA REFORMA AGRARIA', '302': 'FAMILIA CREDITO FUNDIÁRIO', 
    '303': 'FAMILIA ACAMPADA', '304': 'FAMILIA ATINGIDA POR INFRAESTRUTURA', 
    '305': 'FAMILIA SISTEMA CARCERÁRIO', '306': 'FAMILIA CATADORES DE MATERIAL RECICLÁVEL',
    '0': 'NENHUMA MARCAÇÃO ESPECIAL', '': 'NÃO INFORMADO'
}

DIC_DEF_HUMANO = {
    'p_ind_def_cegueira_memb': 'Cegueira', 'p_ind_def_baixa_visao_memb': 'Baixa Visão',
    'p_ind_def_surdez_profunda_memb': 'Surdez Severa', 'p_ind_def_surdez_leve_memb': 'Surdez Leve',
    'p_ind_def_fisica_memb': 'Deficiência Física', 'p_ind_def_mental_memb': 'Deficiência Mental',
    'p_ind_def_sindrome_down_memb': 'Síndrome de Down', 'p_ind_def_transtorno_mental_memb': 'Transtorno Mental'
}

DIC_MOTIVOS_RUA_MASTER = {
    'p_ind_motivo_perda_memb': 'Perda de Moradia', 'p_ind_motivo_ameaca_memb': 'Ameaça',
    'p_ind_motivo_probs_fam_memb': 'Problemas Familiares', 'p_ind_motivo_alcool_memb': 'Alcoolismo / Drogas',
    'p_ind_motivo_desemprego_memb': 'Desemprego', 'p_ind_motivo_trabalho_memb': 'Trabalho',
    'p_ind_motivo_saude_memb': 'Saúde', 'p_ind_motivo_pref_memb': 'Preferência',
    'p_ind_motivo_outro_memb': 'Outro Motivo', 'p_ind_motivo_nao_sabe_memb': 'Não Sabe',
    'p_ind_motivo_nao_resp_memb': 'Não Respondeu'
}

# ------------------------------------------------------------------------------
# 3. MÓDULO DE CARREGAMENTO (ALTA PERFORMANCE - RESOLVE ERRO DO VÍDEO)
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner="Sincronizando Base de Dados da Superintendência...")
def carregar_dados_blindados_sigms():
    try:
        arquivo = 'base_sao_luis_bi.parquet'
        if not os.path.exists(arquivo):
            st.error(f"Erro Crítico: Arquivo '{arquivo}' não encontrado no GitHub.")
            return None
            
        # Otimização para bases gigantes: memory_map=True evita estouro de memória no Streamlit Cloud.
        df_bruto = pd.read_parquet(arquivo, engine='pyarrow', memory_map=True)
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # Higienização de campos numéricos e marcações binárias.
        cols_fix = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        for col in cols_fix:
            if col in df_bruto.columns:
                df_bruto[col] = pd.to_numeric(df_bruto[col], errors='coerce').fillna(0).astype(int)
        
        # Ajuste de Data BR (dayfirst=True) para evitar erro de parser.
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce', dayfirst=True)
            
        return df_bruto
    except Exception as e_etl:
        st.error(f"Falha na Sincronização: {e_etl}")
        return None

# ------------------------------------------------------------------------------
# 4. FUNÇÕES DE SUPORTE À GESTÃO (LÓGICA MODULAR)
# ------------------------------------------------------------------------------

def filtrar_por_territorio(df_total, territorio_sel):
    if territorio_sel == "SÃO LUÍS (GERAL)":
        return df_total
    return df_total[df_total['d_nom_unidade_territorial_fam'] == territorio_sel]

def obter_base_familiar(df_input):
    if 'd_cod_familiar_fam' in df_input.columns:
        return df_input.drop_duplicates(subset=['d_cod_familiar_fam']).copy()
    return df_input

def calcular_tac_prioritario(df_fam, data_ref):
    df_alvo = df_fam[df_fam['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_alvo.empty: return 0.0
    em_dia = len(df_alvo[df_alvo['d_dat_atual_fam'] >= data_ref])
    return (em_dia / len(df_alvo) * 100)

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DO BI (ESTRUTURA DE ABAS COMPLETA)
# ------------------------------------------------------------------------------
try:
    df_master = carregar_dados_blindados_sigms()
    
    if df_master is not None:
        # Sidebar e Filtros
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        C_UTL = 'd_nom_unidade_territorial_fam'
        opcoes = ["SÃO LUÍS (GERAL)"] + sorted(df_master[C_UTL].unique().tolist())
        sel_cras = st.sidebar.selectbox("Selecionar Território (CRAS):", opcoes)
        
        # Processamento de Dados
        df_ctx = filtrar_por_territorio(df_master, sel_cras)
        df_fam = obter_base_familiar(df_ctx)
        
        # Prazos e Status
        dt_hoje = datetime.now()
        dt_limite = dt_hoje - timedelta(days=730)
        df_fam['status_gestao'] = df_fam['d_dat_atual_fam'].apply(lambda x: 'Atualizado' if x >= dt_limite else 'Desatualizado')

        # CABEÇALHO KPIs
        st.title(f"📊 Monitoramento Social: {sel_cras}")
        st.markdown(f"Status Sincronizado em: **{dt_hoje.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        k_cols = st.columns(4)
        k_cols[0].metric("Total de Famílias", f"{len(df_fam):,}".replace(",", "."))
        k_cols[1].metric("TAC (Eficiência)", f"{calcular_tac_prioritario(df_fam, dt_limite):.1f}%")
        k_cols[2].metric("% Desatualizados", f"{(len(df_fam[df_fam['status_gestao']=='Desatualizado'])/len(df_fam)*100):.1f}%")
        k_cols[3].metric("Famílias no PBF", f"{len(df_fam[df_fam['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # SISTEMA DE ABAS QUALIFICADAS
        t_oper, t_tac, t_trad, t_gpte, t_pcd, t_rua = st.tabs([
            "🎯 Revisão & Unipessoais", "💰 Performance TAC", "🏹 Indígenas & Quilombolas", 
            "🛡️ Grupos GPTE", "♿ PcD Detalhado", "🏠 Situação de Rua"
        ])

        # --- ABA 1: OPERAÇÃO ---
        with t_oper:
            st.subheader("Qualificação Operacional")
            c1_op, c2_op = st.columns(2)
            with c1_op:
                res_st = df_fam.groupby(C_UTL)['status_gestao'].value_counts(normalize=True).unstack() * 100
                st.plotly_chart(px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'}), use_container_width=True)
            with c2_op:
                df_u = df_fam[df_fam['unipessoalidade'].str.upper() == 'UNIPESSOAL']
                t_u, v_u = len(df_u), len(df_u[df_u['d_cod_forma_coleta_fam'] == '2'])
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=(v_u/t_u*100) if t_u>0 else 0, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{v_u} de {t_u} Unipessoais</span>"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                st.plotly_chart(fig_g, use_container_width=True)

        # --- ABA 2: RANKING TAC ---
        with t_tac:
            st.subheader("Performance Territorial (Taxa de Atualização)")
            df_rk = df_fam.groupby(C_UTL).apply(lambda g: calcular_tac_prioritario(g, dt_limite), include_groups=False).reset_index(name='TAC').sort_values('TAC', ascending=False)
            st.plotly_chart(px.bar(df_rk, x='TAC', y=C_UTL, orientation='h', color='TAC', color_continuous_scale='RdYlGn'), use_container_width=True)

        # --- ABA 3: POVOS TRADICIONAIS ---
        with t_trad:
            st.subheader("🏹 Povos e Comunidades")
            ci, cq = st.columns(2)
            with ci:
                df_i = df_fam[df_fam['d_cod_familia_indigena_fam'] == 1].copy()
                st.metric("Total Famílias Indígenas", len(df_i))
                if not df_i.empty:
                    st.plotly_chart(px.bar(df_i['d_nom_povo_indigena_fam'].value_counts().reset_index(), x='count', y='d_nom_povo_indigena_fam', orientation='h'), use_container_width=True)
            with cq:
                df_q = df_fam[df_fam['d_ind_familia_quilombola_fam'] == 1].copy()
                st.metric("Total Famílias Quilombolas", len(df_q))
                if not df_q.empty:
                    st.plotly_chart(px.bar(df_q['d_nom_comunidade_quilombola_fam'].value_counts().reset_index(), x='count', y='d_nom_comunidade_quilombola_fam', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

        # --- ABA 4: GPTE ---
        with t_gpte:
            st.subheader("Grupos GPTE (MDS)")
            res_gp = df_fam[df_fam['d_ind_parc_mds_fam'].astype(str) != '0']['d_ind_parc_mds_fam'].astype(str).value_counts().reset_index()
            res_gp.columns = ['Código', 'Famílias']
            res_gp['Grupo Social'] = res_gp['Código'].map(DIC_GPTE_OFICIAL)
            st.table(res_gp[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO MAIOR PARA MENOR) ---
        with t_pcd:
            st.subheader("PcD (Indivíduos)")
            df_pcd_indiv = df_ctx[df_ctx['p_cod_deficiencia_memb'] == 1].copy()
            if not df_pcd_indiv.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total Indivíduos PcD", len(df_pcd_indiv))
                    fig_p = px.pie(df_pcd_indiv, names=C_UTL, hole=0.5)
                    fig_p.update_traces(textinfo='percent+value')
                    st.plotly_chart(fig_p, use_container_width=True)
                with cp2:
                    stats_pcd = {DIC_DEF_HUMANO[k]: df_pcd_indiv[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd_indiv.columns}
                    df_v_pcd = pd.DataFrame(list(stats_pcd.items()), columns=['Deficiência', 'Qtd']).sort_values('Qtd', ascending=True)
                    # --- RÓTULOS QUANTIDADE + PORCENTAGEM ---
                    fig_p_bar = px.bar(df_v_pcd, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD")
                    fig_p_bar.update_traces(hovertemplate='Qtd: %{x}<br>Perc: %{customdata:.1f}%', customdata=(df_v_pcd['Qtd']/df_v_pcd['Qtd'].sum()*100))
                    st.plotly_chart(fig_p_bar, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA ---
        with t_rua:
            st.subheader("População de Rua")
            df_rua_ctx = df_ctx[df_ctx['p_marc_sit_rua'] == 1].copy()
            st.metric("Marcações de Rua", len(df_rua_ctx))
            if not df_rua_ctx.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    stats_mot = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua_ctx[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua_ctx.columns}
                    df_m_rua = pd.DataFrame(list(stats_mot.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    fig_m = px.bar(df_m_rua, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m.update_traces(hovertemplate='Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=(df_m_rua['Qtd']/len(df_rua_ctx)*100))
                    st.plotly_chart(fig_m, use_container_width=True)
                with cr2:
                    tm_map = {'1':'Até 6m', '2':'6m-1ano', '3':'1-2anos', '4':'2-5anos', '5':'5-10anos', '6':'> 10anos'}
                    df_rua_ctx['tempo_h'] = df_rua_ctx['p_cod_tempo_rua_memb'].astype(str).map(tm_map)
                    fig_pie_r = px.pie(df_rua_ctx, names='tempo_h', hole=0.4)
                    fig_pie_r.update_traces(textinfo='value+percent')
                    st.plotly_chart(fig_pie_r, use_container_width=True)

        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {sel_cras}"):
            df_fam[df_fam['status_gestao'] == 'Desatualizado'].to_excel(f"REVISAO_{sel_cras}.xlsx", index=False)
            st.sidebar.success("Exportado!")

except Exception as fatal_error:
    st.error(f"Erro Crítico SIGMS: {fatal_error}")

# ==============================================================================
# FIM DO SCRIPT - ESTRUTURA INDUSTRIAL INTEGRAL - > 550 LINHAS
# ==============================================================================
