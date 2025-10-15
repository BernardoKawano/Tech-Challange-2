# 🤖 GUIA DE INSTALAÇÃO - OLLAMA (LLM LOCAL)

**Data:** 15 de Outubro de 2025  
**Opção Escolhida:** Ollama Local (100% GRÁTIS)

---

## 📋 PRÉ-REQUISITOS

- ✅ Windows 10/11
- ✅ 8GB+ RAM (ideal: 16GB)
- ✅ ~4GB espaço em disco (para o modelo)
- ✅ Internet (só para download inicial)

---

## 📥 PASSO 1: BAIXAR OLLAMA

### **Opção A: Instalador Windows (RECOMENDADO)**

1. Acesse: https://ollama.ai/download/windows
2. Baixe o instalador: `OllamaSetup.exe`
3. Execute como administrador
4. Siga o assistente de instalação
5. Pronto!

### **Opção B: Via PowerShell**

```powershell
# Baixar e instalar
winget install Ollama.Ollama
```

---

## ✅ PASSO 2: VERIFICAR INSTALAÇÃO

Abra o PowerShell e digite:

```powershell
ollama --version
```

**Saída esperada:**
```
ollama version is 0.x.x
```

---

## 🤖 PASSO 3: BAIXAR MODELO

Escolha um modelo (recomendo começar com o menor):

### **Opção A: Llama 2 7B (RECOMENDADO)** 
- Tamanho: ~3.8GB
- RAM: 8GB
- Qualidade: Boa
- Velocidade: Rápida

```powershell
ollama pull llama2
```

### **Opção B: Mistral 7B** 
- Tamanho: ~4.1GB
- RAM: 8GB
- Qualidade: Muito boa
- Velocidade: Rápida

```powershell
ollama pull mistral
```

### **Opção C: Llama 2 13B** 
- Tamanho: ~7.3GB
- RAM: 16GB
- Qualidade: Excelente
- Velocidade: Mais lenta

```powershell
ollama pull llama2:13b
```

**ATENÇÃO:** O download pode demorar 10-30 minutos dependendo da sua internet!

---

## 🧪 PASSO 4: TESTAR

Teste se o modelo está funcionando:

```powershell
ollama run llama2 "Olá, como você está?"
```

**Saída esperada:**
```
Olá! Estou funcionando bem, obrigado por perguntar. Como posso ajudá-lo hoje?
```

Para sair do chat, digite: `/bye`

---

## 🔧 PASSO 5: INICIAR SERVIDOR

O Ollama precisa estar rodando em background. Execute:

```powershell
ollama serve
```

**DEIXE ESTA JANELA ABERTA!** O servidor precisa estar rodando para o Python se conectar.

**Ou** configure para iniciar automaticamente:
1. Pressione `Win + R`
2. Digite: `shell:startup`
3. Crie um atalho para: `C:\Program Files\Ollama\ollama.exe serve`

---

## 📦 PASSO 6: INSTALAR BIBLIOTECA PYTHON

No seu projeto:

```powershell
cd "Tech Challange #2\Tech-Challange-2"
pip install ollama
```

---

## ✅ PASSO 7: TESTAR INTEGRAÇÃO PYTHON

Crie um arquivo de teste:

```python
# test_ollama.py
import ollama

response = ollama.chat(model='llama2', messages=[
  {
    'role': 'user',
    'content': 'Por favor, diga olá em uma frase curta.',
  },
])
print(response['message']['content'])
```

Execute:
```powershell
python test_ollama.py
```

**Saída esperada:**
```
Olá! Como posso ajudá-lo hoje?
```

---

## 🎛️ COMANDOS ÚTEIS

### **Ver modelos instalados:**
```powershell
ollama list
```

### **Remover modelo (liberar espaço):**
```powershell
ollama rm llama2
```

### **Ver status do servidor:**
```powershell
ollama ps
```

### **Parar servidor:**
```powershell
# Ctrl+C na janela do servidor
```

---

## 🐛 TROUBLESHOOTING

### **Erro: "ollama: command not found"**
- Reinicie o PowerShell/Terminal
- Verifique se instalou corretamente
- Tente reiniciar o PC

### **Erro: "Failed to load model"**
- Certifique-se que o servidor está rodando: `ollama serve`
- Verifique se o modelo foi baixado: `ollama list`
- Tente baixar novamente: `ollama pull llama2`

### **Muito lento ou trava**
- Seu PC pode não ter RAM suficiente
- Tente um modelo menor (llama2:7b em vez de 13b)
- Feche outros programas

### **Erro: "Connection refused"**
- O servidor não está rodando
- Execute: `ollama serve` em outra janela

---

## 📊 COMPARAÇÃO DE MODELOS

| Modelo | Tamanho | RAM Mín. | Qualidade | Velocidade | Uso |
|--------|---------|----------|-----------|------------|-----|
| llama2 | 3.8GB | 8GB | Boa | Rápida | Geral |
| mistral | 4.1GB | 8GB | Muito Boa | Rápida | Recomendado |
| llama2:13b | 7.3GB | 16GB | Excelente | Lenta | Qualidade máxima |
| codellama | 3.8GB | 8GB | Boa | Rápida | Código |
| phi | 1.6GB | 4GB | OK | Muito Rápida | PC fraco |

---

## 🎯 CHECKLIST DE INSTALAÇÃO

- [ ] Baixar e instalar Ollama
- [ ] Verificar instalação (`ollama --version`)
- [ ] Baixar modelo (`ollama pull llama2`)
- [ ] Testar modelo (`ollama run llama2 "teste"`)
- [ ] Iniciar servidor (`ollama serve`)
- [ ] Instalar biblioteca Python (`pip install ollama`)
- [ ] Testar integração Python
- [ ] ✅ PRONTO PARA USAR!

---

## 💡 DICAS

1. **Primeira geração é sempre mais lenta** (modelo carrega na memória)
2. **Deixe o servidor rodando** durante todo o uso
3. **Modelos menores são mais rápidos** mas menos precisos
4. **Se travar, reinicie** o servidor Ollama
5. **Monitor de desempenho** pode mostrar uso de RAM/CPU

---

## 🔗 LINKS ÚTEIS

- Site oficial: https://ollama.ai/
- Documentação: https://github.com/ollama/ollama
- Modelos disponíveis: https://ollama.ai/library
- Python client: https://github.com/ollama/ollama-python

---

## ⏱️ TEMPO ESTIMADO

- Download Ollama: 2-5 minutos
- Instalação: 1-2 minutos
- Download modelo: 10-30 minutos (depende da internet)
- Testes: 2-5 minutos

**TOTAL: ~20-40 minutos**

---

## 🎉 PRONTO!

Após completar todos os passos, você terá:
- ✅ Ollama instalado
- ✅ Modelo baixado
- ✅ Servidor rodando
- ✅ Python conectado
- ✅ Pronto para gerar instruções e relatórios!

**Próximo passo:** Executar o sistema completo com LLM! 🚀

---

**Criado em:** 15/10/2025  
**Atualizado em:** 15/10/2025  
**Versão:** 1.0

