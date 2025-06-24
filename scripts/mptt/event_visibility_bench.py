import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from mptt_tests.models import SubgroupUnit, Event

logger = setup_logger('mptt')


@timed
def build_deep_tree_with_event():
    SubgroupUnit.objects.all().delete()
    Event.objects.all().delete()

    root = SubgroupUnit.objects.create(name="Root")
    all_nodes = []

    for i in range(3):
        l1 = SubgroupUnit.objects.create(name=f"L1-{i}", parent=root)
        for j in range(3):
            l2 = SubgroupUnit.objects.create(name=f"L2-{i}-{j}", parent=l1)
            for k in range(5):
                l3 = SubgroupUnit.objects.create(name=f"L3-{i}-{j}-{k}", parent=l2)
                for m in range(10):
                    l4 = SubgroupUnit.objects.create(name=f"L4-{i}-{j}-{k}-{m}", parent=l3)
                    for n in range(15):
                        l5 = SubgroupUnit.objects.create(name=f"L5-{i}-{j}-{k}-{m}-{n}", parent=l4)
                        all_nodes.append(l5)

    SubgroupUnit.objects.rebuild()

    # Evento visível para todos os filhos de L2-0-0
    l2_0_0 = SubgroupUnit.objects.get(name="L2-0-0")
    event = Event.objects.create(name="Evento Hierárquico")
    event.subgroup_unit.add(l2_0_0)

    return l2_0_0, all_nodes


def get_visible_events_for(node: SubgroupUnit):
    return Event.objects.filter(
        subgroup_unit__tree_id=node.tree_id,
        subgroup_unit__lft__lte=node.lft,
        subgroup_unit__rght__gte=node.rght,
    ).distinct()


def main():
    logger.info("🏗️ Construindo árvore 3–3–5–10–15 e evento associado...")
    (branch_root, all_nodes), duration = build_deep_tree_with_event()
    logger.info(f"✅ Árvore com {len(all_nodes)} folhas criada em {duration:.2f}s")

    visible_node = next(
        node for node in all_nodes if node.get_ancestors().filter(name=branch_root.name).exists()
    )
    invisible_node = next(
        node for node in all_nodes if not node.get_ancestors().filter(name=branch_root.name).exists()
    )

    logger.info(f"🔍 Testando visibilidade do evento em nó filho de {branch_root.name}...")
    visible_events, t1 = timed(get_visible_events_for)(visible_node)
    logger.info(f"✅ {visible_node.name} vê {visible_events.count()} evento(s) em {t1:.6f}s")

    logger.info(f"🔍 Testando visibilidade do evento em nó fora de {branch_root.name}...")
    invisible_events, t2 = timed(get_visible_events_for)(invisible_node)
    logger.info(f"❌ {invisible_node.name} vê {invisible_events.count()} evento(s) em {t2:.6f}s")


if __name__ == "__main__":
    main()
