import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from treebeard_tests.models import SubgroupUnit, Event

logger = setup_logger('treebeard')


@timed
def build_deep_tree_with_event():
    SubgroupUnit.objects.all().delete()
    Event.objects.all().delete()

    root = SubgroupUnit.add_root(name="Root")
    all_nodes = []

    for i in range(3):
        l1 = root.add_child(name=f"L1-{i}")
        for j in range(3):
            l2 = l1.add_child(name=f"L2-{i}-{j}")
            for k in range(5):
                l3 = l2.add_child(name=f"L3-{i}-{j}-{k}")
                for m in range(10):
                    l4 = l3.add_child(name=f"L4-{i}-{j}-{k}-{m}")
                    for n in range(15):
                        l5 = l4.add_child(name=f"L5-{i}-{j}-{k}-{m}-{n}")
                        all_nodes.append(l5)

    # Evento visível para todos os filhos de L2-0-0
    l2_0_0 = SubgroupUnit.objects.get(name="L2-0-0")
    event = Event.objects.create(name="Evento Hierárquico")
    event.subgroup_unit.add(l2_0_0)

    return l2_0_0, all_nodes


def get_visible_events_for(node: SubgroupUnit):
    # Queremos eventos associados a subgroup_units que são ancestrais ou o próprio node
    ancestors_and_self = node.get_ancestors()
    return Event.objects.filter(subgroup_unit__in=ancestors_and_self).distinct()


def main():
    logger.info("🏗️ Construindo árvore 3–3–5–10–15 e evento associado...")
    (branch_root, all_nodes), duration = build_deep_tree_with_event()
    logger.info(f"✅ Árvore com {len(all_nodes)} folhas criada em {duration:.2f}s")

    visible_node = next(
        node for node in all_nodes if branch_root in node.get_ancestors()
    )
    invisible_node = next(
        node for node in all_nodes if branch_root not in node.get_ancestors()
    )

    logger.info(f"🔍 Testando visibilidade do evento em nó filho de {branch_root.name}...")
    visible_events, t1 = timed(get_visible_events_for)(visible_node)
    logger.info(f"✅ {visible_node.name} vê {visible_events.count()} evento(s) em {t1:.6f}s")

    logger.info(f"🔍 Testando visibilidade do evento em nó fora de {branch_root.name}...")
    invisible_events, t2 = timed(get_visible_events_for)(invisible_node)
    logger.info(f"❌ {invisible_node.name} vê {invisible_events.count()} evento(s) em {t2:.6f}s")


if __name__ == "__main__":
    main()
