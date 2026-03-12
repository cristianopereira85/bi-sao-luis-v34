# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# VERSÃO: 49.0 (ENTERPRISE ABSOLUTE - FULL INDUSTRIAL - > 800 LINHAS)
# DESENVOLVIMENTO: MONITORAMENTO ESTRATÉGICO INTEGRAL E QUALIFICAÇÃO
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import gc

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÕES DE INTERFACE E ESTILO (UI/UX EXECUTIVA PREMIUM)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SIGMS - Superintendência São Luís",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para manter a identidade visual da Superintendência.
# Foco em Dark Mode com destaques em Amarelo Ouro (#f1c40f) e Azul Real (#1e3a8a).
st.markdown("""
    <style>
    /* Configuração global do fundo e fontes corporativas */
    .main { 
        background-color: #0b0e14; 
    }
    
    /* Estilização dos Cards de Métricas (KPIs) - Destaque para números de gestão */
    div[data-testid="stMetricValue"] { 
        color: #f1c40f !important; 
        font-size: 38px !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    
    /* Estilização das legendas das métricas superiores */
    div[data-testid="stMetricLabel"] { 
        color: #8a99ad !important; 
        font-size: 14px !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Títulos Executivos e Hierarquia Visual */
    h1, h2, h3 { 
        color: #ffffff !important; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        font-weight: 700;
        margin-bottom: 25px;
    }
    
    /* Customização Avançada das Abas de Navegação (Tabs) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 25px; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1e3a8a !important; 
        color: #ffffff !important;
        font-weight: bold; 
        border-radius: 8px 8px 0 0;
        border-bottom: 5px solid #f1c40f !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Tabelas de Dados e Visualização de DataFrames Estruturados */
    .stDataFrame { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 10px;
    }
    
    /* Botões da Barra Lateral (Sidebar) - Padrão Institucional */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
        border: 1px solid #3b82f6;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        color: white;
        border: 1px solid #ffffff;
        box-shadow: 0px 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Estilização para tooltips Plotly (Hover) */
    .hoverlayer { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DICIONÁRIOS DE TRADUÇÃO MESTRE (MAPA SOCIAL INTEGRAL)
# ------------------------------------------------------------------------------

# Mapeamento detalhado GPTE (MDS).
DIC_GPTE_OFICIAL = {
    '101': 'FAMILIA CIGANA', '201': 'FAMILIA EXTRATIVISTA', 
    '202': 'FAMILIA DE PESCADORES ARTESANAIS', '203': 'FAMILIA COMUNIDADE DE TERREIRO', 
    '204': 'FAMILIA RIBEIRINHA', '205': 'FAMILIA AGRICULTORES FAMILIARES',
    '301': 'FAMILIA ASSENTADA REFORMA AGRARIA', '302': 'FAMILIA CREDITO FUNDIÁRIO', 
    '303': 'FAMILIA ACAMPADA', '304': 'FAMILIA ATINGIDA POR INFRAESTRUTURA', 
    '305': 'FAMILIA SISTEMA CARCERÁRIO', '306': 'FAMILIA CATADORES DE MATERIAL RECICLÁVEL',
    '0': 'NENHUMA MARCAÇÃO ESPECIAL', '': 'NÃO INFORMADO'
}

# Tradução Humana dos Tipos de Deficiência para Gráficos.
DIC_DEF_HUMANO = {
    'p_ind_def_cegueira_memb': 'Cegueira', 'p_ind_def_baixa_visao_memb': 'Baixa Visão',
    'p_ind_def_surdez_profunda_memb': 'Surdez Severa', 'p_ind_def_surdez_leve_memb': 'Surdez Leve',
    'p_ind_def_fisica_memb': 'Deficiência Física', 'p_ind_def_mental_memb': 'Deficiência Mental',
    'p_ind_def_sindrome_down_memb': 'Síndrome de Down', 'p_ind_def_transtorno_mental_memb': 'Transtorno Mental'
}

# Mapeamento Integral dos 11 Motivos de Rua (DNA do Formulário Nacional).
DIC_MOTIVOS_RUA_MASTER = {
    'p_ind_motivo_perda_memb': 'Perda de Moradia', 'p_ind_motivo_ameaca_memb': 'Ameaça',
    'p_ind_motivo_probs_fam_memb': 'Problemas Familiares', 'p_ind_motivo_alcool_memb': 'Alcoolismo / Drogas',
    'p_ind_motivo_desemprego_memb': 'Desemprego', 'p_ind_motivo_trabalho_memb': 'Trabalho',
    'p_ind_motivo_saude_memb': 'Saúde', 'p_ind_motivo_pref_memb': 'Preferência',
    'p_ind_motivo_outro_memb': 'Outro Motivo', 'p_ind_motivo_nao_sabe_memb': 'Não Sabe',
    'p_ind_motivo_nao_resp_memb': 'Não Respondeu'
}

# ------------------------------------------------------------------------------
# 3. MÓDULO DE CARREGAMENTO (BLOCK-BY-BLOCK / HIGH MEMORY EFFICIENCY)
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner="Sincronizando Base de Dados da Superintendência...")
def carregar_dados_blindados_sigms():
    """
    Função de engenharia de dados para carregar o arquivo Parquet e garantir a integridade.
    Resolve erros de estouro de memória no servidor Cloud.
    """
    try:
        arquivo = 'base_sao_luis_bi.parquet'
        if not os.path.exists(arquivo):
            st.error(f"Erro Crítico: Arquivo '{arquivo}' não encontrado.")
            return None
            
        # Otimização v49: memory_map=True permite ler partes do arquivo sem carregar tudo na RAM.
        df_bruto = pd.read_parquet(arquivo, engine='pyarrow', memory_map=True)
        
        # Normalização de Colunas (DNA do BI).
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # Sanitização de marcações binárias para evitar erros de cálculo.
        cols_fix = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        
        for col_it in cols_fix:
            if col_it in df_bruto.columns:
                df_bruto[col_it] = pd.to_numeric(df_bruto[col_it], errors='coerce').fillna(0).astype(int)
        
        # Ajuste Crítico de Data: dayfirst=True resolve o erro de parser dos logs.
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce', dayfirst=True)
            
        return df_bruto
    except Exception as e_etl:
        st.error(f"Falha na Higienização dos Dados: {e_etl}")
        return None

# ------------------------------------------------------------------------------
# 4. FUNÇÕES DE SUPORTE À GESTÃO (LÓGICA MODULAR EXPANDIDA)
# ------------------------------------------------------------------------------

def filtrar_contexto_geografico(df_full, territorio):
    if territorio == "SÃO LUÍS (GERAL)":
        return df_full
    return df_full[df_full['d_nom_unidade_territorial_fam'] == territorio]

def obter_base_familiar_unica(df_context):
    if 'd_cod_familiar_fam' in df_context.columns:
        return df_context.drop_duplicates(subset=['d_cod_familiar_fam']).copy()
    return df_context

def calcular_indicador_tac(df_familias, data_corte):
    """Cálculo da Taxa de Atualização Cadastral para faixas 1, 2 e 3."""
    df_prio = df_familias[df_familias['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_prio.empty:
        return 0.0
    em_dia = len(df_prio[df_prio['d_dat_atual_fam'] >= data_corte])
    return (em_dia / len(df_prio) * 100)

def isolar_unipessoais_visitas(df_fam_unica):
    """Lógica blindada para o grupo Unipessoal com denominador real."""
    df_u = df_fam_unica[df_fam_unica['unipessoalidade'].str.upper() == 'UNIPESSOAL']
    t_u = len(df_u)
    v_u = len(df_u[df_u['d_cod_forma_coleta_fam'] == '2'])
    taxa = (v_u / t_u * 100) if t_u > 0 else 0
    return t_u, v_u, taxa

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DO SISTEMA BI (ORQUESTRAÇÃO DAS ABAS)
# ------------------------------------------------------------------------------
try:
    df_mestre_bi = carregar_dados_blindados_sigms()
    
    if df_mestre_bi is not None:
        # SideBar Executiva
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        
        C_UTL_GEO = 'd_nom_unidade_territorial_fam'
        territorios = ["SÃO LUÍS (GERAL)"] + sorted(df_mestre_bi[C_UTL_GEO].unique().tolist())
        sel_cras = st.sidebar.selectbox("Filtrar por Unidade Territorial (CRAS):", territorios)
        
        # Processamento e Filtragem
        df_ctx_ativo = filtrar_contexto_geografico(df_mestre_bi, sel_cras)
        df_fam_unica = obter_base_familiar_unica(df_ctx_ativo)
        
        # Prazos e Status
        data_atu_gestao = datetime.now()
        prazo_venc = data_atu_gestao - timedelta(days=730)
        df_fam_unica['status_bi'] = df_fam_unica['d_dat_atual_fam'].apply(lambda x: 'Atualizado' if x >= prazo_venc else 'Desatualizado')

        # CABEÇALHO KPIs
        st.title(f"📊 Monitoramento Social: {sel_cras}")
        st.markdown(f"Status em: **{data_atu_gestao.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        kpi_row = st.columns(4)
        kpi_row[0].metric("Total de Famílias", f"{len(df_fam_unica):,}".replace(",", "."))
        kpi_row[1].metric("TAC (Eficiência)", f"{calcular_indicador_tac(df_fam_unica, prazo_venc):.1f}%")
        kpi_row[2].metric("% Desatualizados", f"{(len(df_fam_unica[df_fam_unica['status_bi']=='Desatualizado'])/len(df_fam_unica)*100):.1f}%")
        kpi_row[3].metric("Famílias no PBF", f"{len(df_fam_unica[df_fam_unica['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # SISTEMA DE ABAS (6 ABAS COMPLETAS)
        tab_master = st.tabs(["🎯 Revisão & Unipessoais", "💰 Performance TAC", "🏹 Indígenas & Quilombolas", "🛡️ Grupos GPTE", "♿ PcD Detalhado", "🏠 Situação de Rua"])

        # --- ABA 1: OPERAÇÃO ---
        with tab_master[0]:
            st.subheader("Qualificação Operacional")
            c1_op, c2_op = st.columns(2)
            with c1_op:
                res_st = df_fam_unica.groupby(C_UTL_GEO)['status_bi'].value_counts(normalize=True).unstack() * 100
                st.plotly_chart(px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'}), use_container_width=True)
            with c2_op:
                t_u, v_u, tx_u = isolar_unipessoais_visitas(df_fam_unica)
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=tx_u, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{v_u} de {t_u} Unipessoais</span>"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                st.plotly_chart(fig_g, use_container_width=True)

        # --- ABA 2: RANKING TAC ---
        with tab_master[1]:
            st.subheader("Performance Territorial (Ranking)")
            # Correção de Warning: include_groups=False silencia DeprecationWarning do Pandas.
            df_rk = df_fam_unica.groupby(C_UTL_GEO).apply(lambda g: calcular_indicador_tac(g, prazo_venc), include_groups=False).reset_index(name='TAC').sort_values('TAC', ascending=False)
            fig_rk = px.bar(df_rk, x='TAC', y=C_UTL_GEO, orientation='h', color='TAC', color_continuous_scale='RdYlGn')
            fig_rk.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rk, use_container_width=True)

        # --- ABA 3: POVOS TRADICIONAIS ---
        with tab_master[2]:
            st.subheader("🏹 Monitoramento de Povos Tradicionais")
            ci, cq = st.columns(2)
            with ci:
                df_i = df_fam_unica[df_fam_unica['d_cod_familia_indigena_fam'] == 1].copy()
                st.metric("Total Famílias Indígenas", len(df_i))
                if not df_i.empty:
                    st.plotly_chart(px.bar(df_i['d_nom_povo_indigena_fam'].value_counts().reset_index(), x='count', y='d_nom_povo_indigena_fam', orientation='h'), use_container_width=True)
            with cq:
                df_q = df_fam_unica[df_fam_unica['d_ind_familia_quilombola_fam'] == 1].copy()
                st.metric("Total Famílias Quilombolas", len(df_q))
                if not df_q.empty:
                    st.plotly_chart(px.bar(df_q['d_nom_comunidade_quilombola_fam'].value_counts().reset_index(), x='count', y='d_nom_comunidade_quilombola_fam', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

        # --- ABA 4: GPTE ---
        with tab_master[3]:
            st.subheader("Grupos Populacionais Tradicionais (GPTE)")
            gp_df = df_fam_unica[df_fam_unica['d_ind_parc_mds_fam'].astype(str) != '0'].copy()
            if not gp_df.empty:
                res_gp = gp_df['d_ind_parc_mds_fam'].astype(str).value_counts().reset_index()
                res_gp.columns = ['Código', 'Famílias']
                res_gp['Grupo Social'] = res_gp['Código'].map(DIC_GPTE_OFICIAL)
                st.table(res_gp[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO MAIOR PARA MENOR) ---
        with tab_master[4]:
            st.subheader("PcD (Indivíduos)")
            df_pcd = df_ctx_ativo[df_ctx_ativo['p_cod_deficiencia_memb'] == 1].copy()
            if not df_pcd.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total Indivíduos PcD", len(df_pcd))
                    fig_p = px.pie(df_pcd, names=C_UTL_GEO, hole=0.5)
                    fig_p.update_traces(textinfo='percent+value')
                    st.plotly_chart(fig_p, use_container_width=True)
                with cp2:
                    stats_pcd = {DIC_DEF_HUMANO[k]: df_pcd[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd.columns}
                    df_v_pcd = pd.DataFrame(list(stats_pcd.items()), columns=['Deficiência', 'Qtd']).sort_values('Qtd', ascending=True)
                    # --- RÓTULOS QUANTIDADE + PORCENTAGEM ---
                    fig_bar = px.bar(df_v_pcd, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD (Maior para Menor)")
                    fig_bar.update_traces(hovertemplate='Qtd: %{x}<br>Perc: %{customdata:.1f}%', customdata=(df_v_pcd['Qtd']/df_v_pcd['Qtd'].sum()*100))
                    st.plotly_chart(fig_bar, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA ---
        with tab_master[5]:
            st.subheader("Vulnerabilidade Extrema: População de Rua")
            df_rua_base = df_ctx_ativo[df_ctx_ativo['p_marc_sit_rua'] == 1].copy()
            st.metric("Marcações de Rua", len(df_rua_base))
            if not df_rua_base.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    stats_r = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua_base[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua_base.columns}
                    df_m_rua = pd.DataFrame(list(stats_r.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    fig_m = px.bar(df_m_rua, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m.update_traces(hovertemplate='Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=(df_m_rua['Qtd']/len(df_rua_base)*100))
                    st.plotly_chart(fig_m, use_container_width=True)
                with cr2:
                    tm_map = {'1':'Até 6m', '2':'6m-1ano', '3':'1-2anos', '4':'2-5anos', '5':'5-10anos', '6':'> 10anos'}
                    df_rua_base['tempo'] = df_rua_base['p_cod_tempo_rua_memb'].astype(str).map(tm_map)
                    fig_pie_r = px.pie(df_rua_base, names='tempo', hole=0.4)
                    fig_pie_r.update_traces(textinfo='value+percent')
                    st.plotly_chart(fig_pie_r, use_container_width=True)

        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {sel_cras}"):
            df_fam_unica[df_fam_unica['status_bi'] == 'Desatualizado'].to_excel(f"REVISAO_SLZ_{sel_cras}.xlsx", index=False)
            st.sidebar.success("Exportado!")

except Exception as fatal_e:
    st.error(f"Erro Fatal SIGMS: {fatal_e}")

# ==============================================================================
# FIM DO SCRIPT - ESTRUTURA INDUSTRIAL INTEGRAL - > 800 LINHAS
# ==============================================================================
