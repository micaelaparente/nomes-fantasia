-- CNPJs do município do Rio de Janeiro no retrato de janeiro de 2026 da Receita Federal, pela Base dos Dados
-- (https://basedosdados.org, tabela br_me_cnpj.estabelecimentos): os ativos e os que fecharam a partir de 2021.
-- Os fechados vêm junto; a etapa 01_universo.py fica só com os ativos (situação cadastral 2). O filtro de município é
-- pelo código IBGE do Rio (3304557).
--
-- Colunas: cnpj, nome_fantasia, cnae (principal), cnaes_secundarios (separados por vírgula), situacao_cadastral
-- (2 = ativa), inicio (abertura), fim (data em que deixou de estar ativa; vazio se ativa), logradouro (tipo + nome),
-- numero, cep (só dígitos), bairro (como declarado; quando vazio, o mais frequente do mesmo CEP) e bairro_imputado
-- (true nesses casos).

WITH base AS (
  SELECT
    cnpj,
    NULLIF(TRIM(nome_fantasia), '') AS nome_fantasia,
    cnae_fiscal_principal AS cnae,
    cnae_fiscal_secundaria AS cnaes_secundarios,
    situacao_cadastral,
    data_inicio_atividade AS inicio,
    IF(situacao_cadastral = '2', NULL, data_situacao_cadastral) AS fim,
    TRIM(UPPER(CONCAT(IFNULL(tipo_logradouro, ''), ' ', IFNULL(logradouro, '')))) AS logradouro,
    NULLIF(TRIM(numero), '') AS numero,
    NULLIF(REGEXP_REPLACE(CAST(cep AS STRING), r'\D', ''), '') AS cep,
    NULLIF(TRIM(UPPER(bairro)), '') AS bairro_original
  FROM `basedosdados.br_me_cnpj.estabelecimentos`
  WHERE ano = 2026 AND mes = 1             -- retrato de 2026-01-11
    AND id_municipio = '3304557'           -- Rio de Janeiro
),
-- bairro mais frequente de cada CEP, usado para preencher os nulos
bairro_por_cep AS (
  SELECT cep, ARRAY_AGG(bairro_original ORDER BY n DESC LIMIT 1)[OFFSET(0)] AS bairro_cep
  FROM (
    SELECT cep, bairro_original, COUNT(*) AS n
    FROM base
    WHERE cep IS NOT NULL AND bairro_original IS NOT NULL
    GROUP BY 1, 2
  )
  GROUP BY cep
)

SELECT
  b.* EXCEPT (bairro_original),
  COALESCE(b.bairro_original, c.bairro_cep) AS bairro,
  b.bairro_original IS NULL AND c.bairro_cep IS NOT NULL AS bairro_imputado
FROM base b
LEFT JOIN bairro_por_cep c USING (cep)
WHERE b.fim IS NULL OR b.fim >= '2021-01-01'  -- ativos + fechados no período
