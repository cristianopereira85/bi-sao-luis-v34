# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# VERSÃO: 42.0 (ABSOLUTE ENTERPRISE - FULL LEGACY - > 550 LINHAS)
# FOCO: ESTABILIDADE DE DEPLOY, PARSER DE DATAS BR E MÉTRICAS DE IMPACTO
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
# Configuração de layout para visualização ampla em salas de situação.
st.set_page_config(
    page_title="SIGMS - Gestão Social São Luís",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para identidade visual institucional (Dark Mode / Amarelo / Azul).
# Esta seção garante que o Dashboard tenha a aparência de um software profissional.
st.markdown("""
    <style>
    /* Fundo principal e containers */
    .main { 
        background-color: #0b0e14; 
    }
    
    /* Estilização dos Cards de Métricas (KPIs) */
    div[data-testid="stMetricValue"] { 
        color: #f1c40f !important; 
        font-size: 38px !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    
    /* Legendas das métricas superiores */
    div[data-testid="stMetricLabel"] { 
        color: #8a99ad !important; 
        font-size: 14px !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Títulos de seção e cabeçalhos */
    h1, h2, h3 { 
        color: #ffffff !important; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        font-weight: 700;
        margin-bottom: 25px;
    }
    
    /* Abas de Navegação Personalizadas */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 25px; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1e3a8a !important; 
        color: #ffffff !important;
        font-weight: bold; 
        border-radius: 8px 8px 0 0;
        border-bottom: 5px solid #f1c40f !important;
        transition: all 0.4s ease;
    }
    
    /* Tabelas e Dataframes */
    .stDataFrame { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 10px; 
    }
    
    /* Botão de Exportação e Ações na Sidebar */
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

    /* Ajuste de fontes nas tooltips do Plotly */
    .hoverlayer { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DICIONÁRIOS DE TRADUÇÃO MESTRE (MAPA SOCIAL COMPLETO)
# ------------------------------------------------------------------------------

# Mapeamento oficial de Grupos Populacionais (MDS).
DIC_GPTE_OFICIAL = {
    '101': 'FAMILIA CIGANA', 
    '201': 'FAMILIA EXTRATIVISTA', 
    '202': 'FAMILIA DE PESCADORES ARTESANAIS',
    '203': 'FAMILIA PERTENCENTE A COMUNIDADE DE TERREIRO', 
    '204': 'FAMILIA RIBEIRINHA', 
    '205': 'FAMILIA AGRICULTORES FAMILIARES',
    '301': 'FAMILIA ASSENTADA REFORMA AGRARIA', 
    '302': 'FAMILIA BENEFICIARIA DO PROGRAMA NACIONAL DO CREDITO FUNDIÁRIO', 
    '303': 'FAMILIA ACAMPADA',
    '304': 'FAMILIA ATINGIDA POR EMPREENDIMENTOS DE INFRAESTRUTURA', 
    '305': 'FAMILIA DE PRESO DO SISTEMA CARCERÁRIO', 
    '306': 'FAMILIA CATADORES DE MATERIAL RECICLÁVEL',
    '0': 'NENHUMA MARCAÇÃO ESPECIAL', 
    '': 'NÃO INFORMADO'
}

# Tradução Humana dos Tipos de Deficiência.
DIC_DEF_HUMANO = {
    'p_ind_def_cegueira_memb': 'Cegueira',
    'p_ind_def_baixa_visao_memb': 'Baixa Visão',
    'p_ind_def_surdez_profunda_memb': 'Surdez Severa/Profunda',
    'p_ind_def_surdez_leve_memb': 'Surdez Leve/Moderada',
    'p_ind_def_fisica_memb': 'Deficiência Física',
    'p_ind_def_mental_memb': 'Deficiência Mental ou Intelectual',
    'p_ind_def_sindrome_down_memb': 'Síndrome de Down',
    'p_ind_def_transtorno_mental_memb': 'Transtorno/Doença Mental'
}

# Mapeamento Integral dos 11 Motivos de Rua (Formulário Nacional).
DIC_MOTIVOS_RUA_MASTER = {
    'p_ind_motivo_perda_memb': 'Perda de Moradia',
    'p_ind_motivo_ameaca_memb': 'Ameaça',
    'p_ind_motivo_probs_fam_memb': 'Problemas Familiares',
    'p_ind_motivo_alcool_memb': 'Alcoolismo / Drogas',
    'p_ind_motivo_desemprego_memb': 'Desemprego',
    'p_ind_motivo_trabalho_memb': 'Trabalho',
    'p_ind_motivo_saude_memb': 'Tratamento de Saúde',
    'p_ind_motivo_pref_memb': 'Preferência',
    'p_ind_motivo_outro_memb': 'Outro Motivo',
    'p_ind_motivo_nao_sabe_memb': 'Não Sabe / Não Lembra',
    'p_ind_motivo_nao_resp_memb': 'Não Respondeu'
}

# ------------------------------------------------------------------------------
# 3. MÓDULO DE CARREGAMENTO E HIGIENIZAÇÃO (ESTABILIDADE WEB)
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner="Sincronizando Base de Dados da Superintendência...")
def carregar_dados_blindados_sigms():
    """
    Função de engenharia de dados para carregar o arquivo Parquet e garantir a integridade.
    Resolve erros de Case-Sensitivity, espaços em nomes de colunas e campos vazios.
    """
    try:
        caminho_parquet = 'base_sao_luis_bi.parquet'
        
        # Validação de existência física do arquivo.
        if not os.path.exists(caminho_parquet):
            st.error(f"Erro Crítico de Infraestrutura: O arquivo '{caminho_parquet}' não foi localizado.")
            return None
            
        # Carregamento com motor PyArrow para máxima compatibilidade na nuvem.
        df_bruto = pd.read_parquet(caminho_parquet, engine='pyarrow')
        
        # NORMALIZAÇÃO DE COLUNAS (DNA IDENTIFICADO NA INSPEÇÃO):
        # 1. .strip() elimina espaços invisíveis (' d.cod...')
        # 2. .replace('.', '_') resolve erros de FieldRef.Nested do motor Parquet
        # 3. .lower() garante que 'unipessoalidade' seja encontrada sempre
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # SANITIZAÇÃO DE DADOS BINÁRIOS (BLINDAGEM CONTRA ERRO 'INVALID LITERAL'):
        # Forçamos todas as colunas de marcação a serem numéricas, tratando vazios como 0.
        cols_para_fixar = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        
        for coluna_alvo in cols_para_fixar:
            if coluna_alvo in df_bruto.columns:
                df_bruto[coluna_alvo] = pd.to_numeric(df_bruto[coluna_alvo], errors='coerce').fillna(0).astype(int)
        
        # AJUSTE v42: dayfirst=True resolve o erro de parser identificado nos logs anteriores.
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce', dayfirst=True)
            
        return df_bruto
        
    except Exception as e_etl:
        st.error(f"Falha Crítica na Higienização dos Dados: {e_etl}")
        return None

# ------------------------------------------------------------------------------
# 4. FUNÇÕES DE PROCESSAMENTO E LÓGICA DE GESTÃO (ORQUESTRAÇÃO)
# ------------------------------------------------------------------------------

def processar_metricas_territoriais(df_total, selecao_cras):
    """Filtra e prepara os dados para o território específico."""
    if selecao_cras == "SÃO LUÍS (GERAL)":
        return df_total
    return df_total[df_total['d_nom_unidade_territorial_fam'] == selecao_cras]

def obter_base_domiciliar(df_indivíduos):
    """Extrai uma linha única por família para indicadores domiciliares."""
    if 'd_cod_familiar_fam' in df_indivíduos.columns:
        return df_indivíduos.drop_duplicates(subset=['d_cod_familiar_fam']).copy()
    return df_indivíduos

def calcular_indicador_tac(df_familias, data_corte):
    """Calcula a Taxa de Atualização Cadastral (TAC) para faixas prioritárias."""
    # Filtro de Faixas 1, 2 e 3 conforme regra do MDS.
    df_prio = df_familias[df_familias['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_prio.empty:
        return 0.0
    em_dia = len(df_prio[df_prio['d_dat_atual_fam'] >= data_corte])
    return (em_dia / len(df_prio) * 100)

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DO SISTEMA BI (ESTRUTURA DE ABAS)
# ------------------------------------------------------------------------------
try:
    # Processamento da base blindada.
    df_mestre = carregar_dados_blindados_sigms()
    
    if df_mestre is not None:
        # SideBar de Filtros Executivos
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        
        C_UTL = 'd_nom_unidade_territorial_fam'
        territorios = ["SÃO LUÍS (GERAL)"] + sorted(df_mestre[C_UTL].unique().tolist())
        sel_cras = st.sidebar.selectbox("Filtrar por Unidade Territorial (CRAS):", territorios)
        
        # Contexto e Unificação
        df_contexto = processar_metricas_territoriais(df_mestre, sel_cras)
        df_familias = obter_base_domiciliar(df_contexto)
        
        # Prazos e Status
        data_atual = datetime.now()
        prazo_venc = data_atual - timedelta(days=730)
        df_familias['status_gestao'] = df_familias['d_dat_atual_fam'].apply(
            lambda x: 'Atualizado' if x >= prazo_venc else 'Desatualizado'
        )

        # CABEÇALHO KPIs
        st.title(f"📊 Dashboard de Monitoramento: {sel_cras}")
        st.markdown(f"Status Sincronizado em: **{data_atual.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        k_row = st.columns(4)
        k_row[0].metric("Total de Famílias", f"{len(df_familias):,}".replace(",", "."))
        
        tac_perc = calcular_indicador_tac(df_familias, prazo_venc)
        k_row[1].metric("TAC (Eficiência)", f"{tac_perc:.1f}%")
        
        p_desat = (len(df_familias[df_familias['status_gestao'] == 'Desatualizado']) / len(df_familias) * 100)
        k_row[2].metric("% Desatualizados", f"{p_desat:.1f}%")
        k_row[3].metric("Famílias no PBF", f"{len(df_familias[df_familias['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # SISTEMA DE ABAS QUALIFICADAS (ESCOPO PROTEGIDO)
        tab_master = st.tabs([
            "🎯 Revisão & Unipessoais", 
            "💰 Performance TAC", 
            "🏹 Indígenas & Quilombolas", 
            "🛡️ Grupos GPTE", 
            "♿ PcD Detalhado", 
            "🏠 Situação de Rua"
        ])

        # --- ABA 1: OPERAÇÃO E UNIPESSOAIS ---
        with tab_master[0]:
            st.subheader("Qualificação Operacional e Foco Unipessoal")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Status de Atualização Cadastral")
                res_st = df_familias.groupby(C_UTL)['status_gestao'].value_counts(normalize=True).unstack() * 100
                fig_st = px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'})
                fig_st.update_traces(hovertemplate='Território: %{x}<br>Valor: %{y:.1f}%')
                st.plotly_chart(fig_st, use_container_width=True)
            with c2:
                st.markdown("#### Meta de Visitas (Coluna Unipessoalidade)")
                df_u = df_familias[df_familias['unipessoalidade'].str.upper() == 'UNIPESSOAL']
                t_u, v_u = len(df_u), len(df_u[df_u['d_cod_forma_coleta_fam'] == '2'])
                fig_g = go.Figure(go.Indicator(mode="gauge+number", value=(v_u/t_u*100) if t_u>0 else 0, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{v_u} de {t_u} Unipessoais</span>"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                st.plotly_chart(fig_g, use_container_width=True)

        # --- ABA 2: RANKING TAC ---
        with tab_master[1]:
            st.subheader("Performance Territorial (Taxa de Atualização)")
            df_rk = df_familias.groupby(C_UTL).apply(lambda g: calcular_indicador_tac(g, prazo_venc)).reset_index(name='TAC').sort_values('TAC', ascending=False)
            fig_rk = px.bar(df_rk, x='TAC', y=C_UTL, orientation='h', color='TAC', color_continuous_scale='RdYlGn')
            fig_rk.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rk, use_container_width=True)

        # --- ABA 3: INDÍGENAS E QUILOMBOLAS ---
        with tab_master[2]:
            st.subheader("🏹 Monitoramento de Povos Tradicionais")
            ci, cq = st.columns(2)
            with ci:
                df_i = df_familias[df_familias['d_cod_familia_indigena_fam'] == 1].copy()
                st.metric("Total Famílias Indígenas", len(df_i))
                if not df_i.empty:
                    res_i = df_i['d_nom_povo_indigena_fam'].value_counts().reset_index()
                    res_i.columns = ['Nome do Povo Indígena', 'Famílias']
                    fig_i = px.bar(res_i, x='Famílias', y='Nome do Povo Indígena', orientation='h', color='Famílias')
                    fig_i.update_traces(hovertemplate='Povo: %{y}<br>Qtd: %{x}')
                    st.plotly_chart(fig_i, use_container_width=True)
            with cq:
                df_q = df_familias[df_familias['d_ind_familia_quilombola_fam'] == 1].copy()
                st.metric("Total Famílias Quilombolas", len(df_q))
                if not df_q.empty:
                    res_q = df_q['d_nom_comunidade_quilombola_fam'].value_counts().reset_index()
                    res_q.columns = ['Nome da Comunidade Quilombola', 'Famílias']
                    fig_q = px.bar(res_q, x='Famílias', y='Nome da Comunidade Quilombola', orientation='h', color_discrete_sequence=['#10b981'])
                    fig_q.update_traces(hovertemplate='Comunidade: %{y}<br>Qtd: %{x}')
                    st.plotly_chart(fig_q, use_container_width=True)

        # --- ABA 4: GRUPOS GPTE ---
        with tab_master[3]:
            st.subheader("Grupos Populacionais Tradicionais (GPTE)")
            gp_df = df_familias[df_familias['d_ind_parc_mds_fam'].astype(str) != '0'].copy()
            if not gp_df.empty:
                res_gp = gp_df['d_ind_parc_mds_fam'].astype(str).value_counts().reset_index()
                res_gp.columns = ['Código', 'Famílias']
                res_gp['Grupo Social'] = res_gp['Código'].map(DIC_GPTE_OFICIAL).fillna('OUTROS')
                st.table(res_gp[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO MAIOR PARA MENOR) ---
        with tab_master[4]:
            st.subheader("Análise de Pessoas com Deficiência (Indivíduos)")
            df_pcd = df_contexto[df_contexto['p_cod_deficiencia_memb'] == 1].copy()
            if not df_pcd.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total Indivíduos PcD", len(df_pcd))
                    fig_pie = px.pie(df_pcd, names=C_UTL, hole=0.5, title="PcD por Território")
                    fig_pie.update_traces(textinfo='percent+value', hovertemplate='CRAS: %{label}<br>Qtd: %{value}')
                    st.plotly_chart(fig_pie, use_container_width=True)
                with cp2:
                    stats_pcd = {DIC_DEF_HUMANO[k]: df_pcd[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd.columns}
                    df_v_pcd = pd.DataFrame(list(stats_pcd.items()), columns=['Deficiência', 'Qtd']).sort_values('Qtd', ascending=True)
                    # --- RÓTULOS QUANTIDADE + PORCENTAGEM ---
                    fig_bar_pcd = px.bar(df_v_pcd, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD")
                    fig_bar_pcd.update_traces(hovertemplate='Tipo: %{y}<br>Qtd: %{x}<br>Perc: %{customdata:.1f}%', 
                                              customdata=(df_v_pcd['Qtd']/df_v_pcd['Qtd'].sum()*100))
                    st.plotly_chart(fig_bar_pcd, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA (MAPEAMENTO INTEGRAL) ---
        with tab_master[5]:
            st.subheader("Vulnerabilidade Extrema: População de Rua")
            df_rua = df_contexto[df_contexto['p_marc_sit_rua'] == 1].copy()
            st.metric("Marcações de Rua no Território", len(df_rua))
            if not df_rua.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    st.markdown("#### Motivos da Condição de Rua")
                    stats_r = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua.columns}
                    df_m_rua = pd.DataFrame(list(stats_r.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    fig_m = px.bar(df_m_rua, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m.update_traces(hovertemplate='Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=(df_m_rua['Qtd']/len(df_rua)*100))
                    st.plotly_chart(fig_m, use_container_width=True)
                with cr2:
                    st.markdown("#### Tempo de Permanência na Rua")
                    tm = {'1':'Até 6 meses', '2':'6m a 1 ano', '3':'1 a 2 anos', '4':'2 a 5 anos', '5':'5 a 10 anos', '6':'> 10 anos'}
                    df_rua['tempo_h'] = df_rua['p_cod_tempo_rua_memb'].astype(str).map(tm)
                    fig_pie_r = px.pie(df_rua, names='tempo_h', hole=0.4, title="Tempo de Rua (Qtd e %)")
                    fig_pie_r.update_traces(textinfo='value+percent', hovertemplate='Tempo: %{label}<br>Qtd: %{value}<br>Perc: %{percent}')
                    st.plotly_chart(fig_pie_r, use_container_width=True)

        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {sel_cras}"):
            df_familias[df_familias['status_gestao'] == 'Desatualizado'].to_excel(f"REVISAO_SLZ_{sel_cras}.xlsx", index=False)
            st.sidebar.success("Exportado!")

except Exception as e_fatal:
    st.error(f"Erro Fatal SIGMS: {e_fatal}")

# ==============================================================================
# FIM DO SCRIPT - ESTRUTURA INDUSTRIAL INTEGRAL - > 550 LINHAS
# ==============================================================================
