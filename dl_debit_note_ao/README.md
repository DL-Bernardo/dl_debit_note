# Angola Debit Notes & Origin Control (`dl_debit_note_ao`)

Módulo unificado de **Notas de Débito (ND)** para Odoo (v16, v17, v18, v19 e v20), alinhado com o padrão internacional do Odoo (`account_debit_note`) e com os requisitos legais e fiscais da **AGT (Administração Geral Tributária de Angola - SAF-T AO e Faturação Eletrónica)**.

## Principais Funcionalidades

1. **Configuração Automática do Diário `ND`:**
   - Cria ou atualiza automaticamente o diário **Nota de Débito (`ND`)** para todas as empresas na instalação (`post_init_hook`).
   - Configura automaticamente `saft_inv_type = 'ND'` quando o módulo de certificação AGT (`dl_certification_ao`) está instalado.
2. **Duplo Fluxo de Emissão (Wizard + Criação Direta):**
   - **Via Assistente (Wizard):** Botão **"Nota de Débito"** diretamente na fatura ou nota de crédito publicada, pré-selecionando o diário `ND` e exigindo o motivo da emissão.
   - **Via Menu (*Contabilidade → Clientes → Notas de Débito*):** Permite criar Notas de Débito diretamente, pré-selecionando o diário `ND` e habilitando a escolha manual da **Fatura de Origem** (`debit_origin_id`) filtrada pelo cliente.
3. **Controlo e Validação Fiscal (Padrão AGT & Internacional):**
   - Obrigatoriedade da **Fatura de Origem** (`debit_origin_id`) e do **Motivo da Nota de Débito** (`debit_note_reason`) ao confirmar (`action_post`).
   - Validação de que a fatura original pertence ao mesmo cliente e encontra-se publicada (`posted`).
   - Garantia de que o montante total da Nota de Débito é estritamente positivo (`amount_total > 0`).
4. **Integração Nativa com Ecossistema Angola:**
   - Sincroniza automaticamente `invoice_origin`, `invoice_origin_id`, `ref` e `reason_cancel` para impressão nos relatórios PDF (`dl_layouts_ao`), exportação SAF-T AO (`dl_certification_ao`) e submissão de Faturação Eletrónica (`l10n_ao_fe`).
   - Migra automaticamente dados legados do antigo campo `origin_invoice_id` (`custom_debit_note_origin`) para `debit_origin_id`.
