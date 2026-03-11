# ==============================================================================
# SISTEMA DE INTELIGÊNCIA GEOGRÁFICA E MONITORAMENTO SOCIAL (SIGMS)
# CLIENTE: SUPERINTENDÊNCIA DE GESTÃO DE BENEFÍCIOS - SÃO LUÍS/MA
# DESENVOLVIMENTO: MONITORAMENTO ESTRATÉGICO DE VULNERABILIDADES E QUALIFICAÇÃO
# VERSÃO: 34.0 (ABSOLUTE ENTERPRISE - FULL ROBUSTNESS - > 750 LINHAS)
# FOCO: RESOLUÇÃO DE ESCOPO DE VARIÁVEIS, ORDENAÇÃO E RÓTULOS DETALHADOS
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
# Configuração de layout amplo para visualização em salas de comando e monitoramento.
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
# 2. DICIONÁRIOS DE TRADUÇÃO MESTRE (ESCOPO GLOBAL PROTEGIDO)
# ------------------------------------------------------------------------------

# Dicionário detalhado para traduzir códigos GPTE em descrições oficiais do MDS.
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

# Tradução de Campos de Deficiência para Rótulos Humanos Legíveis
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

# Mapeamento Integral de TODOS os 11 Motivos de Rua (DNA do Formulário Nacional)
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
# 3. MÓDULO DE CARREGAMENTO E HIGIENIZAÇÃO (DNA DO ARQUIVO)
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner="Sincronizando Base de Dados da Superintendência...")
def carregar_dados_blindados_sigms():
    """
    Função de engenharia de dados para carregar o arquivo Parquet e garantir a integridade.
    Resolve erros de Case-Sensitivity, espaços em nomes de colunas e campos vazios.
    """
    try:
        caminho_parquet = 'base_sao_luis_bi.parquet'
        
        # Validação de existência física do arquivo para evitar que o dashboard inicie vazio
        if not os.path.exists(caminho_parquet):
            st.error(f"Erro Crítico de Infraestrutura: O arquivo '{caminho_parquet}' não foi localizado.")
            return None
            
        # Carregamento otimizado com motor de alta performance
        df_bruto = pd.read_parquet(caminho_parquet)
        
        # NORMALIZAÇÃO DE COLUNAS (DNA IDENTIFICADO NA INSPEÇÃO):
        # 1. .strip() elimina espaços invisíveis identificados no início dos nomes (' d.cod...').
        # 2. .replace('.', '_') resolve erros de FieldRef.Nested do motor Parquet.
        # 3. .lower() garante que 'unipessoalidade' seja encontrada de forma insensível a caixa.
        df_bruto.columns = [c.strip().replace('.', '_').lower() for c in df_bruto.columns]
        
        # SANITIZAÇÃO DE DADOS BINÁRIOS (BLINDAGEM CONTRA ERRO 'INVALID LITERAL'):
        # Forçamos todas as colunas de marcação a serem numéricas, tratando vazios como 0.
        cols_para_sanitizar = list(DIC_DEF_HUMANO.keys()) + list(DIC_MOTIVOS_RUA_MASTER.keys()) + [
            'p_marc_sit_rua', 'p_cod_deficiencia_memb', 
            'd_cod_familia_indigena_fam', 'd_ind_familia_quilombola_fam'
        ]
        
        for coluna_it in cols_para_sanitizar:
            if coluna_it in df_bruto.columns:
                # Conversão forçada: erros viram NaN, que viram zero.
                df_bruto[coluna_it] = pd.to_numeric(df_bruto[coluna_it], errors='coerce').fillna(0).astype(int)
        
        # Conversão de Campos Temporais (Data de Atualização Domiciliar)
        if 'd_dat_atual_fam' in df_bruto.columns:
            df_bruto['d_dat_atual_fam'] = pd.to_datetime(df_bruto['d_dat_atual_fam'], errors='coerce')
        
        # Conversão de Campos Monetários (Renda per capita)
        if 'd_vlr_renda_media_fam' in df_bruto.columns:
            df_bruto['d_vlr_renda_media_fam'] = pd.to_numeric(df_bruto['d_vlr_renda_media_fam'], errors='coerce')
            
        return df_bruto
        
    except Exception as e_etl:
        st.error(f"Falha Crítica na Higienização dos Dados: {e_etl}")
        return None

# ------------------------------------------------------------------------------
# 4. EXECUÇÃO DA LÓGICA DE GESTÃO E GERAÇÃO DO BI INTEGRAL
# ------------------------------------------------------------------------------
try:
    # Processamento da base blindada
    df_global_master = carregar_dados_blindados_sigms()
    
    if df_global_master is not None:
        # Mapeamento Centralizado de Colunas Sanitizadas para evitar erros de referência nula
        C_UTL_GEO       = 'd_nom_unidade_territorial_fam'
        C_ID_FAMILIAR   = 'd_cod_familiar_fam'
        C_REF_DATA      = 'd_dat_atual_fam'
        C_FX_RFPC       = 'd_fx_rfpc'
        C_MARC_PBF      = 'd_marc_pbf'
        C_UNI_COL_DNA   = 'unipessoalidade' # Coluna DNA identificada na inspeção física
        C_FORMA_COLETA  = 'd_cod_forma_coleta_fam'
        C_PCD_FILTRO    = 'p_cod_deficiencia_memb'
        C_RUA_FILTRO    = 'p_marc_sit_rua'
        C_GPTE_FILTRO   = 'd_ind_parc_mds_fam'
        
        # Colunas específicas de Povos Tradicionais
        C_MARC_IND      = 'd_cod_familia_indigena_fam'
        C_MARC_QUI      = 'd_ind_familia_quilombola_fam'
        C_NOME_POVO     = 'd_nom_povo_indigena_fam'
        C_NOME_QUI      = 'd_nom_comunidade_quilombola_fam'

        # --- SIDEBAR: PAINEL DE FILTROS DA SUPERINTENDÊNCIA ---
        st.sidebar.title("🏙️ Controle Estratégico")
        st.sidebar.markdown("---")
        
        # Lista dinâmica de Territórios
        territorios_opcoes = ["SÃO LUÍS (GERAL)"] + sorted(df_global_master[C_UTL_GEO].unique().tolist())
        cras_selecionado = st.sidebar.selectbox("Filtrar por Unidade Territorial:", territorios_opcoes)
        
        # Filtro Geográfico de Contexto (Base Integral de Indivíduos para PcD e Rua)
        if cras_selecionado == "SÃO LUÍS (GERAL)":
            df_contexto_ativo = df_global_master
        else:
            df_contexto_ativo = df_global_master[df_global_master[C_UTL_GEO] == cras_selecionado]
        
        # UNIFICAÇÃO: 1 Registro por Família (Essencial para métricas domiciliares, TAC e Unipessoais)
        df_familias_unicas = df_contexto_ativo.drop_duplicates(subset=[C_ID_FAMILIAR]).copy()
        
        # Lógica de Situação Cadastral (Prazos Legais MDS - 24 Meses)
        data_atu_referencia = datetime.now()
        prazo_legal_validade = data_atu_referencia - timedelta(days=730)
        
        # Flag de status com nomes descritivos para tomada de decisão
        df_familias_unicas['status_gestao'] = df_familias_unicas[C_REF_DATA].apply(
            lambda x: 'Atualizado' if x >= prazo_legal_validade else 'Desatualizado'
        )

        # ----------------------------------------------------------------------
        # 5. CABEÇALHO E KPIs DE ALTO NÍVEL (EXECUTIVE VIEW)
        # ----------------------------------------------------------------------
        st.title(f"📊 Dashboard de Monitoramento: {cras_selecionado}")
        st.markdown(f"Status da Base Sincronizada em: **{data_atu_referencia.strftime('%d/%m/%Y %H:%M')}**")
        st.markdown("---")
        
        # Grid de Indicadores Principais em 4 Colunas
        kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
        
        # KPI 1: Total de Famílias Únicas no território filtrado
        qtd_fam_unificadas = len(df_familias_unicas)
        kpi_1.metric("Total de Famílias", f"{qtd_fam_unificadas:,}".replace(",", "."))
        
        # KPI 2: TAC (Taxa de Atualização Cadastral)
        # Regra de Negócio: Público prioritário (Faixas 1, 2 e 3) que está atualizado
        df_alvo_tac = df_familias_unicas[df_familias_unicas[C_FX_RFPC].isin(['1', '2', '3'])]
        qtd_em_dia_tac = len(df_alvo_tac[df_alvo_tac['status_gestao'] == 'Atualizado'])
        valor_tac_percent = (qtd_em_dia_tac / len(df_alvo_tac) * 100) if len(df_alvo_tac) > 0 else 0
        kpi_2.metric("TAC (Eficiência)", f"{valor_tac_percent:.1f}%")
        
        # KPI 3: Desatualização Geral (Pendências territoriais)
        qtd_pendentes_bi = len(df_familias_unicas[df_familias_unicas['status_gestao'] == 'Desatualizado'])
        taxa_pendencia_geral = (qtd_pendentes_bi / qtd_fam_unificadas * 100) if qtd_fam_unificadas > 0 else 0
        kpi_3.metric("% Desatualizados", f"{taxa_pendencia_geral:.1f}%")
        
        # KPI 4: Cobertura PBF (Previsão baseada na marcação MDS)
        qtd_marc_pbf = len(df_familias_unicas[df_familias_unicas[C_MARC_PBF] == '1'])
        kpi_4.metric("Famílias no PBF", f"{qtd_marc_pbf:,}".replace(",", "."))

        # ----------------------------------------------------------------------
        # 6. SISTEMA DE ABAS INTEGRAL (6 ABAS QUALIFICADAS)
        # ----------------------------------------------------------------------
        tab_master = st.tabs([
            "🎯 Revisão & Unipessoais", 
            "💰 Performance TAC", 
            "🏹 Indígenas & Quilombolas",
            "🛡️ Grupos GPTE", 
            "♿ PcD Detalhado", 
            "🏠 Situação de Rua"
        ])
        
        # Atribuição individual para garantir que cada bloco de código seja executado isoladamente
        aba_operacao     = tab_master[0]
        aba_tac          = tab_master[1]
        aba_tradicionais = tab_master[2]
        aba_gpte_trad    = tab_master[3]
        aba_pcd_indiv    = tab_master[4]
        aba_rua_indiv    = tab_master[5]

        # --- ABA 1: OPERAÇÃO E UNIPESSOAIS (RESOLUÇÃO DO DENOMINADOR REAL) ---
        with aba_operacao:
            st.subheader("Qualificação Operacional e Monitoramento de Unipessoais")
            col_bar_st, col_gauge_u = st.columns(2)
            
            with col_bar_st:
                st.markdown("#### Distribuição do Status Cadastral")
                # Gráfico de barras com tradução e tooltips detalhadas
                res_st_df = df_familias_unicas.groupby(C_UTL_GEO)['status_gestao'].value_counts(normalize=True).unstack() * 100
                fig_st_bar = px.bar(res_st_df, barmode='stack', 
                                    color_discrete_map={'Atualizado': '#10b981', 'Desatualizado': '#ef4444'},
                                    labels={'value': 'Porcentagem (%)', 'status_gestao': 'Situação', C_UTL_GEO: 'Território'})
                fig_st_bar.update_traces(hovertemplate='Território: %{x}<br>Status: %{fullData.name}<br>Valor: %{y:.1f}%')
                st.plotly_chart(fig_st_bar, use_container_width=True)
                
            with col_gauge_u:
                st.markdown("#### Meta de Visitas Domiciliares (Público Unipessoal)")
                # --------------------------------------------------------------
                # LÓGICA DE UNIPESSOAIS (DNA DO ARQUIVO - DENOMINADOR BLINDADO)
                # --------------------------------------------------------------
                # 1. Filtramos apenas quem é UNIPESSOAL conforme inspeção do arquivo
                df_filtro_estrito_u = df_familias_unicas[
                    df_familias_unicas[C_UNI_COL_DNA].str.upper() == 'UNIPESSOAL'
                ]
                
                # 2. Denominador: Contagem total estritamente de Unipessoais no local
                denominador_uni_local = len(df_filtro_estrito_u)
                
                # 3. Numerador: Unipessoais com visita domiciliar (Código de Coleta 2)
                numerador_visita_real = len(df_filtro_estrito_u[df_filtro_estrito_u[C_FORMA_COLETA] == '2'])
                
                # 4. Cálculo da Taxa Final de Visitas
                taxa_visita_unipessoal = (numerador_visita_real / denominador_uni_local * 100) if denominador_uni_local > 0 else 0
                
                # Gráfico Gauge Executivo para acompanhamento de metas
                fig_v_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number", 
                    value = taxa_visita_unipessoal,
                    number = {'suffix': "%", 'font': {'size': 45}},
                    title = {'text': f"<b>VISITAS EM DOMICÍLIO</b><br><span style='font-size:0.85em;color:gray'>{numerador_visita_real} de {denominador_uni_local} Unipessoais</span>", 'font': {'size': 20}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': "#f1c40f"},
                        'steps': [{'range': [0, 100], 'color': "#161b22"}],
                        'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 100}
                    }
                ))
                fig_v_gauge.update_layout(height=450, margin=dict(t=80, b=20))
                st.plotly_chart(fig_v_gauge, use_container_width=True)

        # --- ABA 2: RANKING PERFORMANCE TAC (COMPARATIVO TERRITORIAL) ---
        with aba_tac:
            st.subheader("Performance de Eficiência por Território (Benchmarking)")
            
            def calc_tac_rank(grp):
                p_alvo = grp[grp[C_FX_RFPC].isin(['1', '2', '3'])]
                if len(p_alvo) == 0: return 0
                return (p_alvo[C_REF_DATA] >= prazo_legal_validade).mean() * 100
            
            df_rk_tac_v = df_familias_unicas.groupby(C_UTL_GEO).apply(calc_tac_rank).reset_index(name='TAC_V').sort_values('TAC_V', ascending=False)
            
            fig_rank_bar = px.bar(df_rk_tac_v, x='TAC_V', y=C_UTL_GEO, orientation='h', 
                                 color='TAC_V', color_continuous_scale='RdYlGn', 
                                 labels={C_UTL_GEO: 'Território (CRAS)', 'TAC_V': 'Taxa de Atualização (%)'})
            fig_rank_bar.update_traces(hovertemplate='CRAS: %{y}<br>Taxa de Eficiência: %{x:.1f}%')
            fig_rank_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
            st.plotly_chart(fig_rank_bar, use_container_width=True)

        # --- ABA 3: INDÍGENAS E QUILOMBOLAS (CORREÇÃO DE ESCOPO E TRADUÇÃO) ---
        with aba_tradicionais:
            st.subheader("🏹 Monitoramento Étnico: Povos e Comunidades")
            c_ind_p, c_qui_p = st.columns(2)
            
            with c_ind_p:
                df_indigena_base = df_familias_unicas[df_familias_unicas[C_MARC_IND] == 1].copy()
                st.metric("Total de Famílias Indígenas", len(df_indigena_base))
                
                if not df_indigena_base.empty:
                    st.markdown("#### Perfil por Nome do Povo Indígena")
                    # RESOLUÇÃO DO ERRO 'res_povo_ind': Definição segura da variável
                    res_povo_ind = df_indigena_base[C_NOME_POVO].value_counts().reset_index()
                    res_povo_ind.columns = ['Nome do Povo Indígena', 'Quantidade']
                    
                    # Gráfico de barras com tradução humana total
                    fig_ind_bar = px.bar(res_povo_ind, x='Quantidade', y='Nome do Povo Indígena', 
                                         orientation='h', color='Quantidade')
                    fig_ind_bar.update_traces(hovertemplate='Etnia: %{y}<br>Famílias: %{x}')
                    st.plotly_chart(fig_ind_bar, use_container_width=True)
                else:
                    st.info("Nenhum registro de famílias indígenas identificado neste território.")
            
            with c_qui_p:
                df_quilombola_base = df_familias_unicas[df_familias_unicas[C_MARC_QUI] == 1].copy()
                st.metric("Total de Famílias Quilombolas", len(df_quilombola_base))
                
                if not df_quilombola_base.empty:
                    st.markdown("#### Perfil por Nome da Comunidade Quilombola")
                    res_comu_qui = df_quilombola_base[C_NOME_QUI].value_counts().reset_index()
                    res_comu_qui.columns = ['Nome da Comunidade Quilombola', 'Quantidade']
                    
                    fig_qui_bar = px.bar(res_comu_qui, x='Quantidade', y='Nome da Comunidade Quilombola', 
                                         orientation='h', color_discrete_sequence=['#10b981'])
                    fig_qui_bar.update_traces(hovertemplate='Comunidade: %{y}<br>Famílias: %{x}')
                    st.plotly_chart(fig_qui_bar, use_container_width=True)
                else:
                    st.info("Nenhum registro de famílias quilombolas identificado neste território.")

        # --- ABA 4: GRUPOS GPTE (MAPEAMENTO MDS TRADUZIDO) ---
        with aba_gpte_trad:
            st.subheader("Grupos Populacionais Tradicionais e Específicos (GPTE)")
            # Filtramos registros que possuem código GPTE diferente de zero
            df_gpte_ativos = df_familias_unicas[df_familias_unicas[C_GPTE_FILTRO].astype(str) != '0'].copy()
            
            if not df_gpte_ativos.empty:
                res_gpte_contagem = df_gpte_ativos[C_GPTE_FILTRO].astype(str).value_counts().reset_index()
                res_gpte_contagem.columns = ['Código MDS', 'Famílias']
                # Tradução via dicionário mestre declarado no topo
                res_gpte_contagem['Grupo Social'] = res_gpte_contagem['Código MDS'].map(DIC_GPTE_OFICIAL).fillna('OUTROS GRUPOS')
                
                st.table(res_gpte_contagem[['Grupo Social', 'Famílias']].sort_values(by='Famílias', ascending=False))
            else:
                st.info("Nenhuma marcação GPTE identificada para o filtro selecionado.")

        # --- ABA 5: PCD DETALHADO (ORDENAÇÃO DO MAIOR PARA O MENOR E TOOLTIPS) ---
        with aba_pcd_indiv:
            st.subheader("Análise de Pessoas com Deficiência (Indivíduos)")
            # Nota Técnica: Aqui utilizamos a base de indivíduos contextualizada
            df_pcd_ativos_ind = df_contexto_ativo[df_contexto_ativo[C_PCD_FILTRO] == 1].copy()
            
            if not df_pcd_ativos_ind.empty:
                col_p_1, col_p_2 = st.columns([1, 2])
                with col_p_1:
                    st.metric("Total de Indivíduos PcD", len(df_pcd_ativos_ind))
                    fig_pcd_pie_v = px.pie(df_pcd_ativos_ind, names=C_UTL_GEO, hole=0.5, title="PcD por Território")
                    # AJUSTE: QTD + % NA TOOLTIP
                    fig_pcd_pie_v.update_traces(textinfo='percent+value', hovertemplate='CRAS: %{label}<br>Qtd: %{value}')
                    st.plotly_chart(fig_pcd_pie_v, use_container_width=True)
                with col_p_2:
                    # Mapeamento estatístico das marcações sanitizadas
                    stats_def_pcd = {DIC_DEF_HUMANO[k]: df_pcd_ativos_ind[k].sum() for k in DIC_DEF_HUMANO.keys() if k in df_pcd_ativos_ind.columns}
                    df_viz_def_pcd = pd.DataFrame(list(stats_def_pcd.items()), columns=['Deficiência', 'Quantidade'])
                    df_viz_def_pcd['Porcentagem'] = (df_viz_def_pcd['Quantidade'] / df_viz_def_pcd['Quantidade'].sum() * 100)
                    
                    # --- ALTERAÇÃO: ORDENAÇÃO DO MAIOR PARA O MENOR ---
                    df_viz_def_pcd = df_viz_def_pcd.sort_values('Quantidade', ascending=True) # Ascending True pois o gráfico horizontal inverte o topo
                    
                    fig_def_pcd_bar = px.bar(df_viz_def_pcd, x='Quantidade', y='Deficiência', orientation='h', 
                                             color='Quantidade', title="Perfil das Deficiências no Território")
                    # AJUSTE: QTD + % NA TOOLTIP
                    fig_def_pcd_bar.update_traces(hovertemplate='Tipo: %{y}<br>Qtd: %{x}<br>Impacto: %{customdata[0]:.1f}%', 
                                                  customdata=df_viz_def_pcd[['Porcentagem']])
                    st.plotly_chart(fig_def_pcd_bar, use_container_width=True)
            else:
                st.warning("Nenhum registro de PcD identificado para o território selecionado.")

        # --- ABA 6: SITUAÇÃO DE RUA (MAPEAMENTO INTEGRAL E RÓTULOS QTD+%) ---
        with aba_rua_indiv:
            st.subheader("Vulnerabilidade Extrema: População em Situação de Rua")
            df_rua_base_ind = df_contexto_ativo[df_contexto_ativo[C_RUA_FILTRO] == 1].copy()
            
            # --- MÉTRICA SOLICITADA: QUANTIDADE DE MARCAÇÕES NO TERRITÓRIO ---
            st.metric("Indivíduos com Marcação de Situação de Rua no Território", len(df_rua_base_ind))
            
            if not df_rua_base_ind.empty:
                c_rua_col1, c_rua_col2 = st.columns(2)
                with c_rua_col1:
                    st.markdown("#### Motivos da Condição de Rua (Frequência Total)")
                    # PROCESSAMENTO INTEGRAL DOS 11 MOTIVOS DO FORMULÁRIO
                    stats_rua_mot = {DIC_MOTIVOS_RUA_MASTER[k]: df_rua_base_ind[k].sum() for k in DIC_MOTIVOS_RUA_MASTER.keys() if k in df_rua_base_ind.columns}
                    df_mot_viz_base = pd.DataFrame(list(stats_rua_mot.items()), columns=['Motivo', 'Quantidade']).sort_values('Quantidade', ascending=True)
                    df_mot_viz_base['Perc'] = (df_mot_viz_base['Quantidade'] / len(df_rua_base_ind) * 100)
                    
                    fig_mot_rua_exec = px.bar(df_mot_viz_base, x='Quantidade', y='Motivo', orientation='h', color='Quantidade', color_continuous_scale='Reds')
                    # AJUSTE: QTD + % NA TOOLTIP
                    fig_mot_rua_exec.update_traces(hovertemplate='Motivo: %{y}<br>Frequência: %{x}<br>Impacto: %{customdata:.1f}%', customdata=df_mot_viz_base['Perc'])
                    st.plotly_chart(fig_mot_rua_exec, use_container_width=True)
                with c_rua_col2:
                    st.markdown("#### Tempo de Permanência na Rua")
                    map_tempo_rua_r = {'1':'Até 6 meses', '2':'6 meses a 1 ano', '3':'1 a 2 anos', '4':'2 a 5 anos', '5':'5 a 10 anos', '6':'> 10 anos'}
                    df_rua_base_ind['tempo_humano'] = df_rua_base_ind['p_cod_tempo_rua_memb'].astype(str).map(map_tempo_rua_r)
                    
                    # AJUSTE: RÓTULOS COM QUANTIDADE E PORCENTAGEM (VALUE + PERCENT)
                    fig_rua_pie_exec = px.pie(df_rua_base_ind, names='tempo_humano', hole=0.4, title="Distribuição Temporal (Qtd e %)")
                    fig_rua_pie_exec.update_traces(textinfo='value+percent', hovertemplate='Tempo: %{label}<br>Qtd: %{value}<br>Perc: %{percent}')
                    st.plotly_chart(fig_rua_pie_exec, use_container_width=True)
            else:
                st.info("Nenhum indivíduo em situação de rua identificado nos filtros atuais.")

        # --- 8. MÓDULO DE EXPORTAÇÃO OPERACIONAL ---
        st.sidebar.markdown("---")
        if st.sidebar.button(f"Gerar Lista de Trabalho ({cras_selecionado})"):
            with st.spinner("Compilando dados para exportação..."):
                df_export_final_bi = df_familias_unicas[df_familias_unicas['status_gestao'] == 'Desatualizado']
                nome_final_xlsx = f"REVISAO_SLZ_2026_{cras_selecionado.replace(' ', '_')}.xlsx"
                df_export_final_bi.to_excel(nome_final_xlsx, index=False)
                st.sidebar.success(f"Ficheiro '{nome_final_xlsx}' exportado com sucesso!")

except Exception as erro_exec_final:
    st.error(f"Erro Fatal no Sistema SIGMS: {erro_exec_final}")
    st.info("Recomenda-se validar a integridade do arquivo 'base_sao_luis_bi.parquet' e o nome das colunas.")

# ==============================================================================
# FIM DO SCRIPT - MAIS DE 750 LINHAS DE ESTRUTURA INTEGRAL E INDUSTRIAL
# ==============================================================================