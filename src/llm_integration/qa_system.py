"""
Sistema de Perguntas e Respostas sobre Rotas usando LLM.

Permite que usuários façam perguntas em linguagem natural sobre:
- Rotas otimizadas
- Entregas
- Veículos
- Métricas
- Sugestões de melhorias
"""
import os
from typing import List, Dict, Optional
from datetime import datetime


class QASystem:
    """Sistema de Q&A para consultas sobre rotas em linguagem natural."""
    
    def __init__(self, provider: str = "ollama", model: str = None, api_key: str = None):
        """
        Inicializa o sistema de Q&A.
        
        Args:
            provider: "ollama" (local, grátis) ou "openai" (nuvem, pago)
            model: Nome do modelo
            api_key: API key (apenas para OpenAI)
        """
        self.provider = provider.lower()
        self.context = {}  # Contexto das rotas para consultas
        
        if self.provider == "ollama":
            try:
                import ollama
                self.client = ollama
                self.model = model or "llama2"
                print(f"✅ Sistema Q&A configurado com Ollama: {self.model}")
            except ImportError:
                raise ImportError(
                    "Ollama não instalado! Execute: pip install ollama\n"
                    "E instale o Ollama: https://ollama.ai/download/windows"
                )
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
                self.model = model or "gpt-3.5-turbo"
                print(f"✅ Sistema Q&A configurado com OpenAI: {self.model}")
            except ImportError:
                raise ImportError("OpenAI não instalado! Execute: pip install openai")
        
        else:
            raise ValueError(f"Provider '{provider}' não suportado. Use 'ollama' ou 'openai'")
        
        # Histórico de conversação
        self.conversation_history = []
    
    def load_context(
        self,
        routes: List[Dict],
        vehicles: List[Dict],
        delivery_points: List[Dict],
        metrics: Dict,
        ga_stats: Optional[Dict] = None
    ):
        """
        Carrega o contexto das rotas para consultas.
        
        Args:
            routes: Lista de rotas otimizadas
            vehicles: Lista de veículos
            delivery_points: Lista de pontos de entrega
            metrics: Métricas gerais
            ga_stats: Estatísticas do AG (opcional)
        """
        self.context = {
            'routes': routes,
            'vehicles': vehicles,
            'delivery_points': delivery_points,
            'metrics': metrics,
            'ga_stats': ga_stats or {},
            'loaded_at': datetime.now().isoformat()
        }
        
        print(f"✅ Contexto carregado:")
        print(f"   • {len(routes)} rotas")
        print(f"   • {len(vehicles)} veículos")
        print(f"   • {len(delivery_points)} pontos de entrega")
    
    def ask(self, question: str) -> str:
        """
        Faz uma pergunta em linguagem natural sobre as rotas.
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            Resposta da LLM
        """
        if not self.context:
            return "❌ Erro: Nenhum contexto carregado. Execute load_context() primeiro."
        
        print(f"\n💬 Pergunta: {question}")
        
        # Construir prompt com contexto
        prompt = self._build_qa_prompt(question)
        
        # Chamar LLM
        try:
            if self.provider == "ollama":
                response = self._call_ollama(prompt, question)
            else:  # openai
                response = self._call_openai(prompt, question)
            
            # Adicionar ao histórico
            self.conversation_history.append({
                'question': question,
                'answer': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
        
        except Exception as e:
            error_msg = f"❌ Erro ao processar pergunta: {e}"
            print(error_msg)
            return error_msg
    
    def _call_ollama(self, prompt: str, question: str) -> str:
        """Chama Ollama local."""
        messages = [
            {
                'role': 'system',
                'content': (
                    'Você é um assistente especializado em logística e otimização de rotas. '
                    'Responda perguntas sobre rotas, entregas, veículos e métricas de forma '
                    'CLARA, CONCISA e PRECISA. Use dados do contexto fornecido. '
                    'Se a pergunta não puder ser respondida com os dados disponíveis, '
                    'seja honesto e sugira alternativas. Seja profissional mas amigável.'
                )
            }
        ]
        
        # Adicionar histórico recente (últimas 3 perguntas)
        for conv in self.conversation_history[-3:]:
            messages.append({'role': 'user', 'content': conv['question']})
            messages.append({'role': 'assistant', 'content': conv['answer']})
        
        # Adicionar pergunta atual
        messages.append({'role': 'user', 'content': prompt})
        
        response = self.client.chat(model=self.model, messages=messages)
        return response['message']['content']
    
    def _call_openai(self, prompt: str, question: str) -> str:
        """Chama OpenAI API."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente especializado em logística e otimização de rotas. "
                    "Responda perguntas sobre rotas, entregas, veículos e métricas de forma "
                    "CLARA, CONCISA e PRECISA. Use dados do contexto fornecido. "
                    "Se a pergunta não puder ser respondida com os dados disponíveis, "
                    "seja honesto e sugira alternativas. Seja profissional mas amigável."
                )
            }
        ]
        
        # Adicionar histórico recente
        for conv in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": conv['question']})
            messages.append({"role": "assistant", "content": conv['answer']})
        
        # Adicionar pergunta atual
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _build_qa_prompt(self, question: str) -> str:
        """Constrói prompt com contexto para Q&A."""
        
        # Resumo das rotas
        routes_summary = []
        for i, route in enumerate(self.context['routes'], 1):
            vehicle_name = route.get('vehicle_name', f'Veículo {i}')
            num_points = len(route.get('points', []))
            distance = route.get('distance_km', 0)
            capacity_usage = route.get('capacity_usage_percent', 0)
            
            routes_summary.append(
                f"  • {vehicle_name}: {num_points} entregas, "
                f"{distance:.2f} km, {capacity_usage:.1f}% capacidade"
            )
        
        # Pontos de entrega críticos
        critical_points = [
            p for p in self.context['delivery_points']
            if p.get('priority', '').lower() == 'critico'
        ]
        
        # Construir prompt
        prompt = f"""
CONTEXTO SOBRE AS ROTAS OTIMIZADAS:

RESUMO GERAL:
- Total de veículos: {len(self.context['vehicles'])}
- Total de rotas: {len(self.context['routes'])}
- Total de pontos de entrega: {len(self.context['delivery_points'])}
- Distância total: {self.context['metrics'].get('total_distance', 'N/A')} km
- Entregas críticas: {len(critical_points)}

DETALHES DAS ROTAS:
{chr(10).join(routes_summary)}

MÉTRICAS DE DESEMPENHO:
- Fitness final: {self.context['metrics'].get('fitness', 'N/A')}
- Violações de capacidade: {self.context['metrics'].get('capacity_violations', 0)}
- Violações de autonomia: {self.context['metrics'].get('autonomy_violations', 0)}

ALGORITMO GENÉTICO:
- Gerações: {self.context['ga_stats'].get('total_generations', 'N/A')}
- Crossovers: {self.context['ga_stats'].get('total_crossovers', 'N/A')}
- Mutações: {self.context['ga_stats'].get('total_mutations', 'N/A')}

PERGUNTA DO USUÁRIO:
{question}

INSTRUÇÕES:
- Responda de forma direta e baseada nos dados acima
- Use números e porcentagens quando relevante
- Se precisar de mais informações, seja específico sobre o que falta
- Sugira melhorias quando apropriado
- Mantenha a resposta concisa (máximo 200 palavras)
"""
        
        return prompt
    
    def suggest_improvements(self) -> str:
        """
        Gera sugestões de melhorias baseadas nos padrões identificados.
        
        Returns:
            String com sugestões de melhorias
        """
        if not self.context:
            return "❌ Erro: Nenhum contexto carregado."
        
        question = """
        Com base nos dados de otimização fornecidos, analise os padrões e identifique:
        
        1. PROBLEMAS DETECTADOS:
           - Rotas desbalanceadas?
           - Veículos subutilizados ou sobrecarregados?
           - Entregas críticas em risco?
           - Distâncias muito longas?
        
        2. SUGESTÕES DE MELHORIA:
           - Ajustes na frota (mais/menos veículos)?
           - Mudanças de capacidade?
           - Alteração de prioridades?
           - Redistribuição de entregas?
        
        3. OPORTUNIDADES:
           - Redução de custos?
           - Otimização de tempo?
           - Melhoria no atendimento?
        
        Seja específico e prático. Priorize as 3 melhorias mais impactantes.
        """
        
        print("\n💡 Gerando sugestões de melhoria...")
        response = self.ask(question)
        
        return response
    
    def get_route_summary(self, vehicle_name: Optional[str] = None) -> str:
        """
        Retorna resumo de uma rota específica ou todas.
        
        Args:
            vehicle_name: Nome do veículo (None = todas)
        """
        if vehicle_name:
            question = f"Me dê um resumo detalhado da rota do veículo '{vehicle_name}'."
        else:
            question = "Me dê um resumo geral de todas as rotas otimizadas."
        
        return self.ask(question)
    
    def compare_routes(self, vehicle1: str, vehicle2: str) -> str:
        """
        Compara duas rotas.
        
        Args:
            vehicle1: Nome do primeiro veículo
            vehicle2: Nome do segundo veículo
        """
        question = f"Compare as rotas dos veículos '{vehicle1}' e '{vehicle2}'. Quais são as principais diferenças?"
        return self.ask(question)
    
    def find_bottlenecks(self) -> str:
        """Identifica gargalos e pontos de atenção."""
        question = """
        Analise as rotas e identifique possíveis gargalos:
        - Quais veículos estão próximos do limite de capacidade ou autonomia?
        - Quais entregas críticas estão em rotas longas?
        - Há algum desbalanceamento significativo entre veículos?
        """
        return self.ask(question)
    
    def get_conversation_history(self) -> List[Dict]:
        """Retorna histórico de perguntas e respostas."""
        return self.conversation_history
    
    def clear_history(self):
        """Limpa o histórico de conversação."""
        self.conversation_history = []
        print("✅ Histórico de conversação limpo.")
    
    def export_qa_log(self, filepath: str):
        """
        Exporta o histórico de Q&A para arquivo.
        
        Args:
            filepath: Caminho do arquivo de saída
        """
        if not self.conversation_history:
            print("⚠️ Nenhuma conversação para exportar.")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# HISTÓRICO DE PERGUNTAS E RESPOSTAS\n\n")
            f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de interações: {len(self.conversation_history)}\n\n")
            f.write("="*70 + "\n\n")
            
            for i, conv in enumerate(self.conversation_history, 1):
                f.write(f"## Interação {i}\n\n")
                f.write(f"**Timestamp:** {conv['timestamp']}\n\n")
                f.write(f"**Pergunta:**\n{conv['question']}\n\n")
                f.write(f"**Resposta:**\n{conv['answer']}\n\n")
                f.write("-"*70 + "\n\n")
        
        print(f"✅ Log exportado para: {filepath}")


# Funções auxiliares para uso facilitado

def interactive_qa_session(qa_system: QASystem):
    """
    Inicia uma sessão interativa de perguntas e respostas.
    
    Args:
        qa_system: Instância configurada do QASystem
    """
    print("\n" + "="*70)
    print("💬 SESSÃO INTERATIVA DE PERGUNTAS E RESPOSTAS")
    print("="*70)
    print("\nComandos especiais:")
    print("  • 'sair' ou 'exit' - Encerra a sessão")
    print("  • 'melhorias' - Gera sugestões de melhoria")
    print("  • 'gargalos' - Identifica gargalos")
    print("  • 'historico' - Mostra histórico de perguntas")
    print("  • 'limpar' - Limpa histórico")
    print("\nFaça suas perguntas sobre as rotas otimizadas:\n")
    
    while True:
        try:
            question = input("\n💬 Você: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando sessão. Até logo!")
                break
            
            if question.lower() == 'melhorias':
                print("\n🤖 Assistente:")
                print(qa_system.suggest_improvements())
                continue
            
            if question.lower() == 'gargalos':
                print("\n🤖 Assistente:")
                print(qa_system.find_bottlenecks())
                continue
            
            if question.lower() == 'historico':
                history = qa_system.get_conversation_history()
                print(f"\n📜 Histórico: {len(history)} interações")
                for i, conv in enumerate(history, 1):
                    print(f"\n{i}. {conv['question'][:50]}...")
                continue
            
            if question.lower() == 'limpar':
                qa_system.clear_history()
                continue
            
            # Pergunta normal
            print("\n🤖 Assistente:")
            response = qa_system.ask(question)
            print(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Sessão interrompida. Até logo!")
            break
        
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            continue

