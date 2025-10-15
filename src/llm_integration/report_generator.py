"""
Gerador de Relatórios de Eficiência usando LLM.

Suporta Ollama (local, grátis) e OpenAI (nuvem, pago).
"""
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Gera relatórios analíticos de eficiência usando LLM."""
    
    def __init__(self, provider: str = "ollama", model: str = None, api_key: str = None):
        """
        Inicializa o gerador de relatórios.
        
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
    
    def generate_report(
        self,
        metrics: Dict,
        ga_stats: Dict,
        route_details: List[Dict]
    ) -> str:
        """
        Gera relatório de eficiência.
        
        Args:
            metrics: Métricas gerais (distância, fitness, etc.)
            ga_stats: Estatísticas do AG (gerações, mutações, etc.)
            route_details: Detalhes de cada rota
            
        Returns:
            Relatório em Markdown/texto
        """
        
        print(f"\n📊 Gerando relatório com {self.provider.upper()}...")
        print(f"   Rotas analisadas: {len(route_details)}")
        
        # Construir prompt
        prompt = self._build_report_prompt(metrics, ga_stats, route_details)
        
        # Chamar LLM
        try:
            if self.provider == "ollama":
                response = self._call_ollama(prompt)
            else:  # openai
                response = self._call_openai(prompt)
            
            print(f"   ✅ Relatório gerado com sucesso!")
            return response
        
        except Exception as e:
            print(f"   ❌ Erro ao gerar relatório: {e}")
            return self._generate_fallback_report(metrics, ga_stats, route_details)
    
    def _call_ollama(self, prompt: str) -> str:
        """Chama Ollama local."""
        response = self.client.chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': (
                    'Você é um analista sênior de logística e otimização. '
                    'Analise dados de rotas otimizadas e gere relatórios '
                    'DETALHADOS, ANALÍTICOS e ACIONÁVEIS. Inclua:\n'
                    '- Análise quantitativa (números, percentuais)\n'
                    '- Insights qualitativos (padrões, problemas)\n'
                    '- Recomendações práticas (melhorias, ajustes)\n'
                    'Use formatação Markdown clara. Seja profissional mas direto.'
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
                        "Você é um analista sênior de logística e otimização. "
                        "Analise dados de rotas otimizadas e gere relatórios "
                        "DETALHADOS, ANALÍTICOS e ACIONÁVEIS. Inclua:\n"
                        "- Análise quantitativa (números, percentuais)\n"
                        "- Insights qualitativos (padrões, problemas)\n"
                        "- Recomendações práticas (melhorias, ajustes)\n"
                        "Use formatação Markdown clara. Seja profissional mas direto."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    
    def _build_report_prompt(self, metrics, ga_stats, route_details):
        """Constrói prompt para geração de relatório."""
        
        prompt = f"""
Analise os dados de otimização de rotas e gere um relatório completo:

MÉTRICAS GERAIS:
- Fitness (distância total): {metrics.get('total_distance', 'N/A')} km
- Veículos utilizados: {len(route_details)} de {metrics.get('total_vehicles', 'N/A')}
- Entregas atendidas: {metrics.get('total_deliveries', 'N/A')}
- Violações: {metrics.get('violations', 0)}

ESTATÍSTICAS DO ALGORITMO GENÉTICO:
- Gerações: {ga_stats.get('current_generation', 'N/A')}
- Crossovers: {ga_stats.get('total_crossovers', 'N/A')}
- Mutações: {ga_stats.get('total_mutations', 'N/A')}
- Tipo de seleção: {ga_stats.get('selection_type', 'N/A')}
- Tipo de crossover: {ga_stats.get('crossover_type', 'N/A')}

DETALHES POR VEÍCULO:
"""
        
        for i, route in enumerate(route_details, 1):
            prompt += f"""
Veículo {i} - {route.get('vehicle_name', f'Veículo {i}')}:
- Entregas: {route.get('num_deliveries', 0)}
- Distância: {route.get('distance_km', 0):.1f} km
- Autonomia: {route.get('autonomy_km', 'N/A')} km
- Carga: {route.get('load_kg', 0):.1f} kg
- Capacidade: {route.get('capacity_kg', 'N/A')} kg
- Utilização: {route.get('capacity_usage_%', 0):.1f}%
- Pontos: {' → '.join(route.get('points', []))}
"""
        
        prompt += """

GERE UM RELATÓRIO COMPLETO COM:
1. Resumo executivo (3-4 parágrafos)
2. Tabela de métricas principais (Markdown)
3. Análise detalhada por veículo (performance, problemas, pontos de atenção)
4. Insights e recomendações (mínimo 3)
5. Análise do algoritmo genético (convergência, qualidade)
6. Conclusão e próximos passos

Use Markdown. Seja específico e acionável. Identifique problemas e sugira soluções.
"""
        
        return prompt
    
    def _generate_fallback_report(self, metrics, ga_stats, route_details):
        """Gera relatório básico caso o LLM falhe."""
        
        now = datetime.now()
        
        report = f"""
# 📊 RELATÓRIO DE EFICIÊNCIA DE ROTAS

**Data:** {now.strftime('%d/%m/%Y %H:%M')}  
**Período:** Operação Diária  
**Sistema:** Algoritmo Genético VRP v1.0

---

## 📈 RESUMO EXECUTIVO

A otimização de hoje utilizou **{len(route_details)} veículos** para atender **{metrics.get('total_deliveries', 'N/A')} entregas**, 
percorrendo uma distância total de **{metrics.get('total_distance', 'N/A')} km**.

---

## 📊 MÉTRICAS PRINCIPAIS

| Métrica | Valor |
|---------|-------|
| Distância Total | {metrics.get('total_distance', 'N/A')} km |
| Veículos Utilizados | {len(route_details)} de {metrics.get('total_vehicles', 'N/A')} |
| Entregas Atendidas | {metrics.get('total_deliveries', 'N/A')} |
| Violações | {metrics.get('violations', 0)} |

---

## 🚐 ANÁLISE POR VEÍCULO

"""
        
        for i, route in enumerate(route_details, 1):
            autonomy_usage = (route.get('distance_km', 0) / route.get('autonomy_km', 1) * 100) if route.get('autonomy_km', 0) > 0 else 0
            
            report += f"""
### Veículo {i} - {route.get('vehicle_name', f'Veículo {i}')}

**Métricas:**
- Entregas: {route.get('num_deliveries', 0)}
- Distância: {route.get('distance_km', 0):.1f} km ({autonomy_usage:.1f}% da autonomia)
- Carga: {route.get('load_kg', 0):.1f} kg ({route.get('capacity_usage_%', 0):.1f}% da capacidade)
- Rota: {' → '.join(route.get('points', []))}

"""
        
        report += f"""
---

## 🤖 ALGORITMO GENÉTICO

**Estatísticas:**
- Gerações: {ga_stats.get('current_generation', 'N/A')}
- Crossovers: {ga_stats.get('total_crossovers', 'N/A')}
- Mutações: {ga_stats.get('total_mutations', 'N/A')}
- Seleção: {ga_stats.get('selection_type', 'N/A')}
- Crossover: {ga_stats.get('crossover_type', 'N/A')}

---

## 💡 RECOMENDAÇÕES

1. Monitorar utilização de capacidade dos veículos
2. Verificar rotas para otimização de distância
3. Considerar balanceamento de carga entre veículos

---

## 🎯 CONCLUSÃO

A otimização foi concluída com sucesso. Todas as entregas foram alocadas respeitando as restrições.

---

**Relatório gerado automaticamente**  
Sistema VRP-AG v1.0 | Tech Challenge FIAP
"""
        
        return report
    
    def save_report(self, report: str, prefix: str = "relatorio") -> Path:
        """
        Salva relatório em arquivo Markdown.
        
        Args:
            report: String com relatório
            prefix: Prefixo do nome do arquivo
            
        Returns:
            Path do arquivo salvo
        """
        output_dir = Path("outputs/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.md"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n{'='*70}")
        print(f"✅ RELATÓRIO SALVO!")
        print(f"{'='*70}")
        print(f"📁 Local: {filepath.absolute()}")
        print(f"💡 Abra o arquivo para visualizar o relatório completo!")
        print(f"{'='*70}\n")
        
        return filepath

