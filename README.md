# azure-databricks-mlops


# Create Job
`databricks jobs create --json-file jobs/create-train-job.json`

# TODO
- Dev trabalha no seu repo e sobe alteração abrindo PR
- PR aprovado dispara pipeline que sobe alteração para QA
- Treino do modelo é executado em QA
- Registro realizado em QA
- Pipeline de entrega sobe alteração para PROD
- Treino do modelo é executado em PROD
- Registro realizado em QA