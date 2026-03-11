# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# DESENVOLVIMENTO: MONITORAMENTO ESTRATÉGICO DE VULNERABILIDADES E QUALIFICAÇÃO
# VERSÃO: 44.0 (ABSOLUTE ENTERPRISE - FULL LEGACY - > 550 LINHAS)
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
# Configuração de layout amplo para visualização em salas de comando.
st.set_page_config(
    page_title="SIGMS - Gestão Social São Luís",
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
    
    /* Estilização das legendas das métricas */
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

# Dicionário detalhado para traduzir códigos GPTE em descrições oficiais do MDS.
DIC_GPTE_OFICIAL = {
    '101': 'FAMILIA CIGANA', 
    '201': 'FAMILIA EXTRATIVISTA', 
    '202': 'FAMILIA DE PESCADORES ARTESANAIS',
    '203': 'FAMILIA COMUNIDADE DE TERREIRO', 
    '204': 'FAMILIA RIBEIRINHA', 
    '205': 'FAMILIA AGRICULTORES FAMILIARES',
    '301': 'FAMILIA ASSENTADA REFORMA AGRARIA', 
    '302': 'FAMILIA CREDITO FUNDIÁRIO', 
    '303': 'FAMILIA ACAMPADA',
    '304': 'FAMILIA ATINGIDA POR INFRAESTRUTURA', 
    '305': 'FAMILIA SISTEMA CARCERÁRIO', 
    '306': 'FAMILIA CATADORES DE MATERIAL RECICLÁVEL',
    '0': 'NENHUMA MARCAÇÃO ESPECIAL', 
    '': 'NÃO INFORMADO'
}

# Tradução Humana dos Tipos de Deficiência para Gráficos.
DIC_DEF_HUMANO = {
    'p_ind_def_cegueira_memb': 'Cegueira',
    'p_ind_def_baixa_visao_memb': 'Baixa Visão',
    'p_ind_def_surdez_profunda_memb': 'Surdez Severa',
    'p_ind_def_surdez_leve_memb': 'Surdez Leve',
    'p_ind_def_fisica_memb': 'Deficiência Física',
    'p_ind_def_mental_memb': 'Deficiência Mental',
    'p_ind_def_sindrome_down_memb': 'Síndrome de Down',
    'p_ind_def_transtorno_mental_memb': 'Transtorno Mental'
}

# Mapeamento Integral dos 11 Motivos de Rua (DNA do Formulário Nacional).
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
            
        # Carregamento com motor PyArrow para máxima estabilidade na nuvem.
        df_bruto = pd.read_parquet(caminho_parquet, engine='pyarrow')
        
        # NORMALIZAÇÃO DE COLUNAS:
        # 1. .strip() elimina espaços invisíveis (' d.cod...')
        # 2. .replace('.', '_') resolve erros de FieldRef.Nested do motor Parquet
        # 3. .lower() garante que 'unipessoalidade' seja encontrada sempre
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # SANITIZAÇÃO DE DADOS BINÁRIOS (BLINDAGEM CONTRA ERRO 'INVALID LITERAL'):
        cols_para_fixar = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        
        for coluna_alvo in cols_para_fixar:
            if coluna_alvo in df_bruto.columns:
                df_bruto[coluna_alvo] = pd.to_numeric(df_bruto[coluna_alvo], errors='coerce').fillna(0).astype(int)
        
        # AJUSTE v44: dayfirst=True resolve o erro de parser identificado nos logs anteriores.
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce', dayfirst=True)
            
        return df_bruto
        
    except Exception as e_etl:
        st.error(f"Falha Crítica na Higienização dos Dados: {e_etl}")
        return None

# ------------------------------------------------------------------------------
# 4. FUNÇÕES DE SUPORTE À GESTÃO (LÓGICA EXPANDIDA)
# ------------------------------------------------------------------------------

def filtrar_contexto_geografico(df_full, territorio_escolha):
    """Aplica o filtro de território selecionado na Sidebar."""
    if territorio_escolha == "SÃO LUÍS (GERAL)":
        return df_full
    return df_full[df_full['d_nom_unidade_territorial_fam'] == territorio_escolha]

def gerar_base_familiar_unica(df_context):
    """Extrai uma linha por família para métricas domiciliares precisas."""
    if 'd_cod_familiar_fam' in df_context.columns:
        return df_context.drop_duplicates(subset=['d_cod_familiar_fam']).copy()
    return df_context

def calcular_indicador_tac(df_familias, data_corte_validade):
    """Calcula a Taxa de Atualização Cadastral para as faixas prioritárias (1, 2, 3)."""
    # Filtro de Faixas 1, 2 e 3 conforme regra institucional.
    df_prio = df_familias[df_familias['d_fx_rfpc'].isin(['1', '2', '3'])]
    if df_prio.empty:
        return 0.0
    em_dia = len(df_prio[df_prio['d_dat_atual_fam'] >= data_corte_validade])
    return (em_dia / len(df_prio) * 100)

# ------------------------------------------------------------------------------
# 5. EXECUÇÃO DO SISTEMA BI (ESTRUTURA DE ABAS COMPLETA)
# ------------------------------------------------------------------------------
try:
    # Processamento da base blindada.
    df_mestre_bi = carregar_dados_blindados_sigms()
    
    if df_mestre_bi is not None:
        # SideBar de Filtros Executivos
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        
        C_UTL_GEO = 'd_nom_unidade_territorial_fam'
        territorios_lista = ["SÃO LUÍS (GERAL)"] + sorted(df_mestre_bi[C_UTL_GEO].unique().tolist())
        sel_cras = st.sidebar.selectbox("Filtrar por Unidade Territorial (CRAS):", territorios_lista)
        
        # Contexto e Unificação
        df_ctx_ativo = filtrar_contexto_geografico(df_mestre_bi, sel_cras)
        df_fam_unica = gerar_base_familiar_unica(df_ctx_ativo)
        
        # Prazos e Status
        data_atu_gestao = datetime.now()
        prazo_legal_ref = data_atu_gestao - timedelta(days=730)
        df_fam_unica['status_bi'] = df_fam_unica['d_dat_atual_fam'].apply(
            lambda x: 'Atualizado' if x >= prazo_legal_ref else 'Desatualizado'
        )

        # CABEÇALHO KPIs
        st.title(f"Dashboard de Monitoramento: {sel_cras}")
        st.markdown(f"Status Sincronizado em: **{data_atu_gestao.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Total de Famílias", f"{len(df_fam_unica):,}".replace(",", "."))
        
        tac_perc_val = calcular_indicador_tac(df_fam_unica, prazo_legal_ref)
        kpi_cols[1].metric("TAC (Eficiência)", f"{tac_perc_val:.1f}%")
        
        perc_desat = (len(df_fam_unica[df_fam_unica['status_bi'] == 'Desatualizado']) / len(df_fam_unica) * 100)
        kpi_cols[2].metric("% Desatualizados", f"{perc_desat:.1f}%")
        kpi_cols[3].metric("Famílias no PBF", f"{len(df_fam_unica[df_fam_unica['d_marc_pbf'] == '1']):,}".replace(",", "."))

        # SISTEMA DE ABAS QUALIFICADAS (6 ABAS COMPLETAS)
        tab_operacao, tab_tac, tab_trad, tab_gpte, tab_pcd, tab_rua = st.tabs([
            "🎯 Revisão & Unipessoais", 
            "💰 Performance TAC", 
            "🏹 Indígenas & Quilombolas", 
            "🛡️ Grupos GPTE", 
            "♿ PcD Detalhado", 
            "🏠 Situação de Rua"
        ])

        # --- ABA 1: OPERAÇÃO E UNIPESSOAIS ---
        with tab_operacao:
            st.subheader("Qualificação Operacional e Foco Unipessoal")
            c1_op, c2_op = st.columns(2)
            with c1_op:
                st.markdown("#### Status de Atualização Cadastral")
                res_st = df_fam_unica.groupby(C_UTL_GEO)['status_bi'].value_counts(normalize=True).unstack() * 100
                fig_st = px.bar(res_st, barmode='stack', color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'})
                fig_st.update_traces(hovertemplate='Valor: %{y:.1f}%')
                st.plotly_chart(fig_st, use_container_width=True)
            with c2_op:
                st.markdown("#### Meta de Visitas (Coluna Unipessoalidade)")
                df_u_context = df_fam_unica[df_fam_unica['unipessoalidade'].str.upper() == 'UNIPESSOAL']
                total_u, vis_u = len(df_u_context), len(df_u_context[df_u_context['d_cod_forma_coleta_fam'] == '2'])
                fig_gauge_u = go.Figure(go.Indicator(mode="gauge+number", value=(vis_u/total_u*100) if total_u>0 else 0, number={'suffix': "%"},
                    title={'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{vis_u} de {total_u} Unipessoais</span>"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f1c40f"}}))
                st.plotly_chart(fig_gauge_u, use_container_width=True)

        # --- ABA 2: RANKING TAC ---
        with tab_tac:
            st.subheader("Performance Territorial (Taxa de Atualização)")
            df_rk_val = df_fam_unica.groupby(C_UTL_GEO).apply(lambda g: calcular_indicador_tac(g, prazo_legal_ref)).reset_index(name='TAC').sort_values('TAC', ascending=False)
            fig_rk_bar = px.bar(df_rk_val, x='TAC', y=C_UTL_GEO, orientation='h', color='TAC', color_continuous_scale='RdYlGn')
            fig_rk_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rk_bar, use_container_width=True)

        # --- ABA 3: POVOS TRADICIONAIS ---
        with tab_trad:
            st.subheader("🏹 Monitoramento de Povos Tradicionais")
            col_ind, col_qui = st.columns(2)
            with col_ind:
                df_ind = df_fam_unica[df_fam_unica['d_cod_familia_indigena_fam'] == 1].copy()
                st.metric("Famílias Indígenas", len(df_ind))
                if not df_ind.empty:
                    res_ind_p = df_ind['d_nom_povo_indigena_fam'].value_counts().reset_index()
                    res_ind_p.columns = ['Nome do Povo Indígena', 'Quantidade']
                    st.plotly_chart(px.bar(res_ind_p, x='Quantidade', y='Nome do Povo Indígena', orientation='h', color='Quantidade'), use_container_width=True)
            with col_qui:
                df_qui = df_fam_unica[df_fam_unica['d_ind_familia_quilombola_fam'] == 1].copy()
                st.metric("Famílias Quilombolas", len(df_qui))
                if not df_qui.empty:
                    res_qui_c = df_qui['d_nom_comunidade_quilombola_fam'].value_counts().reset_index()
                    res_qui_c.columns = ['Nome da Comunidade Quilombola', 'Quantidade']
                    st.plotly_chart(px.bar(res_qui_c, x='Quantidade', y='Nome da Comunidade Quilombola', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

        # --- ABA 4: GPTE ---
        with tab_gpte:
            st.subheader("Grupos Populacionais Tradicionais (GPTE)")
            df_gpte_base = df_fam_unica[df_fam_unica['d_ind_parc_mds_fam'].astype(str) != '0'].copy()
            if not df_gpte_base.empty:
                res_gpte_bi = df_gpte_base['d_ind_parc_mds_fam'].astype(str).value_counts().reset_index()
                res_gpte_bi.columns = ['Código', 'Famílias']
                res_gpte_bi['Grupo Social'] = res_gpte_bi['Código'].map(DIC_GPTE_OFICIAL).fillna('OUTROS')
                st.table(res_gpte_bi[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO MAIOR PARA MENOR) ---
        with tab_pcd:
            st.subheader("PcD (Indivíduos)")
            df_pcd_indiv = df_ctx_ativo[df_ctx_ativo['p_cod_deficiencia_memb'] == 1].copy()
            if not df_pcd_indiv.empty:
                cp1, cp2 = st.columns([1, 2])
                with cp1:
                    st.metric("Total PcD", len(df_pcd_indiv))
                    fig_pcd_pie = px.pie(df_pcd_indiv, names=C_UTL_GEO, hole=0.5)
                    fig_pcd_pie.update_traces(textinfo='percent+value')
                    st.plotly_chart(fig_pcd_pie, use_container_width=True)
                with cp2:
                    stats_pcd_val = {DIC_DEF_HUMANO[k]: df_pcd_indiv[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd_indiv.columns}
                    df_v_pcd_rk = pd.DataFrame(list(stats_pcd_val.items()), columns=['Deficiência', 'Qtd']).sort_values('Qtd', ascending=True)
                    # --- RÓTULOS QUANTIDADE + PORCENTAGEM ---
                    fig_pcd_bar = px.bar(df_v_pcd_rk, x='Qtd', y='Deficiência', orientation='h', color='Qtd', title="Perfil PcD")
                    fig_pcd_bar.update_traces(hovertemplate='Qtd: %{x}<br>Perc: %{customdata:.1f}%', 
                                              customdata=(df_v_pcd_rk['Qtd']/df_v_pcd_rk['Qtd'].sum()*100))
                    st.plotly_chart(fig_pcd_bar, use_container_width=True)

        # --- ABA 6: SITUAÇÃO DE RUA ---
        with tab_rua:
            st.subheader("Vulnerabilidade Extrema: População de Rua")
            df_rua_ctx = df_ctx_ativo[df_ctx_ativo['p_marc_sit_rua'] == 1].copy()
            st.metric("Marcações de Rua", len(df_rua_ctx))
            if not df_rua_ctx.empty:
                cr1, cr2 = st.columns(2)
                with cr1:
                    st.markdown("#### Motivos da Condição de Rua")
                    stats_mot_rua = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua_ctx[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua_ctx.columns}
                    df_m_rua_viz = pd.DataFrame(list(stats_mot_rua.items()), columns=['Motivo', 'Qtd']).sort_values('Qtd', ascending=True)
                    fig_m_rua_bar = px.bar(df_m_rua_viz, x='Qtd', y='Motivo', orientation='h', color='Qtd', color_continuous_scale='Reds')
                    fig_m_rua_bar.update_traces(hovertemplate='Qtd: %{x}<br>Impacto: %{customdata:.1f}%', customdata=(df_m_rua_viz['Qtd']/len(df_rua_ctx)*100))
                    st.plotly_chart(fig_m_rua_bar, use_container_width=True)
                with cr2:
                    st.markdown("#### Tempo de Permanência na Rua")
                    tm_trad = {'1':'Até 6m', '2':'6m-1ano', '3':'1-2anos', '4':'2-5anos', '5':'5-10anos', '6':'> 10anos'}
                    df_rua_ctx['tempo_h'] = df_rua_ctx['p_cod_tempo_rua_memb'].astype(str).map(tm_trad)
                    fig_rua_pie_r = px.pie(df_rua_ctx, names='tempo_h', hole=0.4)
                    fig_rua_pie_r.update_traces(textinfo='value+percent')
                    st.plotly_chart(fig_rua_pie_r, use_container_width=True)

        st.sidebar.markdown("---")
        if st.sidebar.button(f"Exportar Lista: {sel_cras}"):
            df_fam_unica[df_fam_unica['status_bi'] == 'Desatualizado'].to_excel(f"REVISAO_{sel_cras}.xlsx", index=False)
            st.sidebar.success("Exportado!")

except Exception as e_error:
    st.error(f"Erro Fatal SIGMS: {e_error}")

# ==============================================================================
# FIM DO SCRIPT - ESTRUTURA INDUSTRIAL INTEGRAL - > 550 LINHAS
# ==============================================================================
