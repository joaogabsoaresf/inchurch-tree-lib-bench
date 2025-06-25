import random
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from treebeard_tests.models import SubgroupUnit, Event
from django.db.models import Count
logger = setup_logger('treebeard_benchmark')


def create_events_with_random_units(n_events=5000, min_units=10, max_units=50):
    # Seleciona os nós intermediários da árvore com profundidade entre 2 e 5
    nodes = SubgroupUnit.objects.filter(depth__gte=2, depth__lte=5)

    events = []
    for i in range(n_events):  # Loop para criar o número total de eventos desejado
        event = Event.objects.create(name=f"Evento-{i}")  # Cria um evento novo com nome único
        # Seleciona aleatoriamente entre min_units e max_units unidades da lista de nós filtrados
        selected_units = random.sample(list(nodes), random.randint(min_units, max_units))
        # Associa essas unidades ao evento (many-to-many)
        event.subgroup_unit.set(selected_units)
        # Guarda o evento na lista para retornar depois
        events.append(event)

    logger.info(f"✅ Criados {n_events} eventos com associações a nós intermediários.")
    return events


def benchmark_event_unit_and_descendants(events):
    results = []

    for event in events:
        # Marca o início da medição de tempo
        start = time.perf_counter()
        # Busca as unidades associadas diretamente ao evento (query no banco)
        base_units = event.subgroup_unit.all()

        all_units = set()
        for unit in base_units:
            # Adiciona a unidade diretamente associada
            all_units.add(unit)
            # Adiciona todos os descendentes da unidade (query para cada unidade)
            all_units.update(unit.get_descendants())

        # Calcula o tempo gasto desde o início
        elapsed = time.perf_counter() - start  

        logger.info(
            f"⏱️ Evento '{event.name}': {len(all_units)} units (incl. descendentes) em {elapsed:.6f}s"
        )

        # Armazena o resultado com o nome do evento, a quantidade total de unidades (diretas + descendentes) e o tempo gasto
        results.append((event.name, len(all_units), elapsed))

    return results


def benchmark_units_with_events(units):
    # Lista que armazenará os resultados do benchmark para cada unidade
    results = []

    # Itera por cada unidade fornecida (pode ser unidades de qualquer nível)
    for unit in units:
        # Marca o tempo inicial da medição
        start = time.perf_counter()

        # Obtém todos os descendentes do nó atual e o próprio nó
        # Isso simula o acesso dos filhos a eventos publicados em níveis superiores
        all_units = set(unit.get_descendants()) | {unit}

        # Consulta todos os eventos que estão associados a qualquer um desses nós
        # .distinct() evita contar o mesmo evento mais de uma vez
        events = Event.objects.filter(subgroup_unit__in=all_units).distinct()

        # Calcula o tempo gasto na consulta
        elapsed = time.perf_counter() - start

        # Loga os dados da execução: nome da unidade, quantidade de nós considerados, eventos encontrados, tempo
        logger.info(
            f"📥 Unidade '{unit.name}' (com {len(all_units)} nós): {events.count()} eventos encontrados em {elapsed:.6f}s"
        )

        # Adiciona os dados coletados à lista de resultados
        results.append((unit.name, len(all_units), events.count(), elapsed))

    # Retorna a lista de resultados para posterior análise
    return results


def run_event_unit_query_benchmark():
    # Event.objects.all().delete()
    logger.info("🚀 Iniciando criação e benchmark de eventos")
    events = create_events_with_random_units()
    results = benchmark_event_unit_and_descendants(events)

    avg_time = sum(r[2] for r in results) / len(results)
    logger.info(f"📊 Tempo médio por evento: {avg_time:.6f} segundos")
    
    print(f"📊 Tempo médio por evento: {avg_time:.6f} segundos")


def benchmark_event_lookup_by_ancestry():
    # Inicia o benchmark com um log informativo
    logger.info("🚀 Iniciando benchmark de busca de eventos por ancestralidade (filho → pai)")

    # Seleciona todos os nós de nível 5 (folhas mais profundas da árvore)
    level_5_nodes = SubgroupUnit.objects.filter(depth=5)

    # Lista para armazenar os resultados do benchmark
    results = []

    # Itera sobre os primeiros 100 nós de nível 5 (limite para evitar execuções longas)
    for node in level_5_nodes[:100]:
        # Começa o benchmark a partir do nó atual
        current_node = node

        # Enquanto houver um nó (ou seja, enquanto não atingir o topo da árvore)
        while current_node is not None:
            # Marca o tempo inicial da medição
            start = time.perf_counter()

            # Obtém todos os ancestrais do nó atual e inclui o próprio nó (acesso do filho aos eventos dos pais)
            ancestry = list(current_node.get_ancestors()) + [current_node]

            # Filtra eventos associados a qualquer um dos nós na ancestralidade
            # .distinct() garante que eventos duplicados (caso ligados a múltiplos ancestrais) não sejam contados mais de uma vez
            events_qs = Event.objects.filter(subgroup_unit__in=ancestry).distinct()

            # Conta quantos eventos foram encontrados
            count = events_qs.count()

            # Calcula o tempo decorrido da query
            elapsed = time.perf_counter() - start

            # Loga o resultado da query para esse nó
            logger.info(
                f"📥 Unidade '{current_node.name}' (depth={current_node.depth}, id={current_node.id}): "
                f"{count} eventos encontrados em {elapsed:.6f}s"
            )

            # Adiciona os dados ao resultado final
            results.append({
                "node_id": current_node.id,           # ID do nó atual
                "node_name": current_node.name,       # Nome do nó atual
                "depth": current_node.depth,          # Nível de profundidade na árvore
                "events_found": count,                # Quantidade de eventos encontrados
                "query_time": elapsed,                # Tempo que a consulta levou
            })

            # Sobe para o nó pai (um nível acima na hierarquia)
            current_node = current_node.get_parent()

    # Retorna todos os resultados do benchmark
    return results


def run_unit_event_query_benchmark():
    logger.info("🚀 Iniciando benchmark de busca de eventos por unidade (com descendentes)")
    units = SubgroupUnit.objects.annotate(
        event_count=Count('subgroup_unit')
    ).filter(event_count__gt=0).order_by('-event_count')[:20]
    
    results = benchmark_units_with_events(units)
    
    avg_time = sum(r[3] for r in results) / len(results)
    logger.info(f"📊 Tempo médio por unidade: {avg_time:.6f} segundos")
    
    print(f"📊 Tempo médio por unidade: {avg_time:.6f} segundos")


if __name__ == "__main__":
    run_event_unit_query_benchmark()
    benchmark_event_lookup_by_ancestry()
    run_unit_event_query_benchmark()
    