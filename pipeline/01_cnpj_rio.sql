-- CNPJs do município do Rio de Janeiro, de qualquer situação cadastral, no recorte mais recente da Receita Federal,
-- pela Base dos Dados (https://basedosdados.org, tabela br_me_cnpj.estabelecimentos).
--
-- ATENÇÃO: reconstrução. A consulta original (out/2026) não foi guardada; esta gera as mesmas colunas, na mesma ordem,
-- a partir do que o CSV original mostra. Conferir contra um extrato novo antes de confiar 100%.
--
-- Colunas:
--   cnpj, nome_fantasia, cnae (principal), cnaes_secundarios (separados por vírgula), situacao_cadastral (2 = ativa),
--   inicio (abertura), fim (data em que deixou de estar ativa; vazio se ativa), logradouro (tipo + nome), numero, cep,
--   bairro (como declarado; quando vazio, o mais comum entre os CNPJs do mesmo CEP), bairro_imputado (true nesses casos)

WITH ultima AS (
  SELECT MAX(data) AS data
  FROM `basedosdados.br_me_cnpj.estabelecimentos`
  WHERE id_municipio = '3304557'
),
est AS (
  SELECT
    e.cnpj,
    e.nome_fantasia,
    e.cnae_fiscal_principal AS cnae,
    e.cnae_fiscal_secundaria AS cnaes_secundarios,
    e.situacao_cadastral,
    e.data_inicio_atividade AS inicio,
    IF(e.situacao_cadastral != '2', e.data_situacao_cadastral, NULL) AS fim,
    TRIM(CONCAT(IFNULL(e.tipo_logradouro, ''), ' ', IFNULL(e.logradouro, ''))) AS logradouro,
    e.numero,
    e.cep,
    NULLIF(TRIM(e.bairro), '') AS bairro
  FROM `basedosdados.br_me_cnpj.estabelecimentos` AS e
  JOIN ultima USING (data)
  WHERE e.id_municipio = '3304557'
),
bairro_do_cep AS (
  SELECT cep, APPROX_TOP_COUNT(bairro, 1)[OFFSET(0)].value AS bairro
  FROM est
  WHERE bairro IS NOT NULL
  GROUP BY cep
)
SELECT
  est.cnpj, est.nome_fantasia, est.cnae, est.cnaes_secundarios, est.situacao_cadastral, est.inicio, est.fim,
  est.logradouro, est.numero, est.cep,
  COALESCE(est.bairro, b.bairro) AS bairro,
  est.bairro IS NULL AND b.bairro IS NOT NULL AS bairro_imputado
FROM est
LEFT JOIN bairro_do_cep AS b USING (cep)
