"""
Gerador de Instruções para Motoristas usando LLM.

Suporta Ollama (local, grátis) e OpenAI (nuvem, pago).
"""
import os
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class InstructionGenerator:
    """Gera instruções detalhadas para motoristas usando LLM."""
    
    def __init__(self, provider: str = "ollama", model: str = None, api_key: str = None):
        """
        Inicializa o gerador de instruções.
        
        Args:
            provider: "ollama" (local, grátis) ou "openai" (nuvem, pago)
            model: Nome do modelo. Se None, usa padrão:
                  - Ollama: "llama2"
                  - OpenAI: "gpt-3.5-turbo"
            api_key: API key (apenas para OpenAI)
        """
        self.provider = provider.lower()
        
        if self.provider == "ollama":
            try:
                import ollama
                self.client = ollama
                self.model = model or "llama2"
                print(f"✅ Ollama configurado com modelo: {self.model}")
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
                print(f"✅ OpenAI configurado com modelo: {self.model}")
            except ImportError:
                raise ImportError("OpenAI não instalado! Execute: pip install openai")
        
        else:
            raise ValueError(f"Provider '{provider}' não suportado. Use 'ollama' ou 'openai'")
    
    def generate_instructions(
        self,
        vehicle: Dict,
        route_points: List[Dict],
        total_distance: float,
        estimated_time: float
    ) -> str:
        """
        Gera instruções detalhadas para uma rota.
        
        Args:
            vehicle: Dados do veículo (nome, capacidade, etc.)
            route_points: Lista de pontos na ordem de visita
            total_distance: Distância total em km
            estimated_time: Tempo estimado em horas
            
        Returns:
            String com instruções formatadas
        """
        
        print(f"\n🤖 Gerando instruções com {self.provider.upper()}...")
        print(f"   Veículo: {vehicle.get('name', 'N/A')}")
        print(f"   Pontos: {len(route_points)}")
        
        # Construir prompt
        prompt = self._build_prompt(vehicle, route_points, total_distance, estimated_time)
        
        # Chamar LLM
        try:
            if self.provider == "ollama":
                response = self._call_ollama(prompt)
            else:  # openai
                response = self._call_openai(prompt)
            
            print(f"   ✅ Instruções geradas com sucesso!")
            return response
        
        except Exception as e:
            print(f"   ❌ Erro ao gerar instruções: {e}")
            return self._generate_fallback_instructions(vehicle, route_points, total_distance, estimated_time)
    
    def _call_ollama(self, prompt: str) -> str:
        """Chama Ollama local."""
        response = self.client.chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': (
                    'Você é um especialista em logística hospitalar. '
                    'Gere instruções DETALHADAS e PRÁTICAS para motoristas '
                    'de entregas médicas. Use linguagem clara, profissional '
                    'e inclua todos os detalhes importantes.'
                )
            },
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        return response['message']['content']
    
    def _call_openai(self, prompt: str) -> str:
        """Chama OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em logística hospitalar. "
                        "Gere instruções DETALHADAS e PRÁTICAS para motoristas "
                        "de entregas médicas. Use linguagem clara, profissional "
                        "e inclua todos os detalhes importantes."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _build_prompt(self, vehicle, route_points, total_distance, estimated_time):
        """Constrói o prompt para o LLM."""
        
        prompt = f"""
Gere instruções detalhadas de entrega para o seguinte cenário:

VEÍCULO:
- Nome: {vehicle.get('name', 'N/A')}
- Capacidade: {vehicle.get('capacity_kg', 'N/A')} kg
- Autonomia: {vehicle.get('autonomy_km', 'N/A')} km
- Tipo: {vehicle.get('vehicle_type', 'Van')}
- Refrigerado: {'Sim' if vehicle.get('is_refrigerated', False) else 'Não'}

RESUMO DA ROTA:
- Total de entregas: {len(route_points)}
- Distância total: {total_distance:.1f} km
- Tempo estimado: {estimated_time:.1f} horas

PONTOS DE ENTREGA (NA ORDEM):
"""
        
        for i, point in enumerate(route_points, 1):
            emoji_priority = {
                'CRITICO': '🔴',
                'ALTO': '🟠',
                'MEDIO': '🟡',
                'BAIXO': '🟢'
            }.get(point.get('priority', 'MEDIO'), '⚪')
            
            prompt += f"""
{i}. {emoji_priority} {point.get('priority', 'N/A')} - {point.get('name', 'N/A')}
   - Endereço: {point.get('address', 'N/A')}
   - Carga: {point.get('weight', 'N/A')} kg
   - Volume: {point.get('volume', 'N/A')} m³
"""
        
        prompt += """

FORMATO DAS INSTRUÇÕES:
1. Cabeçalho com resumo
2. Para cada entrega:
   - Número e prioridade (emoji)
   - Nome do local e endereço
   - Carga e horário estimado
   - Instruções especiais (se aplicável)
   - Dicas de navegação
3. Checklist pré-saída
4. Contatos de emergência

Seja DETALHADO e PRÁTICO. Pense como um motorista de verdade.
Use formatação clara com linhas, espaços e seções bem definidas.
"""
        
        return prompt
    
    def _generate_fallback_instructions(self, vehicle, route_points, total_distance, estimated_time):
        """Gera instruções básicas caso o LLM falhe."""
        
        now = datetime.now()
        
        instructions = f"""
{'='*70}
        INSTRUÇÕES DE ENTREGA - {vehicle.get('name', 'Veículo')}
{'='*70}
Data: {now.strftime('%d/%m/%Y')}
Horário: {now.strftime('%H:%M')}

RESUMO DA ROTA:
- {len(route_points)} entregas programadas
- Distância total: {total_distance:.1f} km
- Tempo estimado: {estimated_time:.1f} horas

{'='*70}
SEQUÊNCIA DE ENTREGAS:
{'='*70}

"""
        
        for i, point in enumerate(route_points, 1):
            emoji_priority = {
                'CRITICO': '🔴',
                'ALTO': '🟠',
                'MEDIO': '🟡',
                'BAIXO': '🟢'
            }.get(point.get('priority', 'MEDIO'), '⚪')
            
            instructions += f"""
{i}. {emoji_priority} {point.get('priority', 'N/A')} - {point.get('name', 'N/A')}
   Endereço: {point.get('address', 'N/A')}
   Carga: {point.get('weight', 'N/A')} kg | Volume: {point.get('volume', 'N/A')} m³
   
"""
        
        instructions += f"""
{'='*70}
CHECKLIST PRÉ-SAÍDA:
{'='*70}
[ ] Verificar combustível (autonomia: {vehicle.get('autonomy_km', 'N/A')} km)
[ ] Conferir carga total
[ ] Documentos de entrega
[ ] Celular carregado
[ ] GPS configurado

{'='*70}
CONTATOS DE EMERGÊNCIA:
{'='*70}
Central de Operações: (11) 3456-7890
WhatsApp: (11) 98765-4321

BOA VIAGEM E ENTREGAS SEGURAS!
{'='*70}
"""
        
        return instructions
    
    def save_instructions(self, instructions: str, filename: str = None) -> Path:
        """
        Salva as instruções em arquivo.
        
        Args:
            instructions: String com instruções
            filename: Nome do arquivo (opcional, gera automaticamente se None)
            
        Returns:
            Path do arquivo salvo
        """
        output_dir = Path("outputs/instructions")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instrucoes_{timestamp}.txt"
        
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"\n{'='*70}")
        print(f"✅ INSTRUÇÕES SALVAS!")
        print(f"{'='*70}")
        print(f"📁 Local: {filepath.absolute()}")
        print(f"💡 Abra o arquivo para visualizar as instruções completas!")
        print(f"{'='*70}\n")
        
        return filepath

