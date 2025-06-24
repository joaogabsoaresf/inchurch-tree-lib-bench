import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from treebeard_tests.models import SubgroupUnit, Event

logger = setup_logger('treebeard')


@timed
def build_tree_and_event():
    SubgroupUnit.objects.all().delete()
    Event.objects.all().delete()

    root = SubgroupUnit.add_root(name="Root")

    for i in range(3):
        l1 = root.add_child(name=f"L1-{i}")
        for j in range(3):
            l2 = l1.add_child(name=f"L2-{i}-{j}")
            for k in range(5):
                l3 = l2.add_child(name=f"L3-{i}-{j}-{k}")
                for m in range(10):
                    l4 = l3.add_child(name=f"L4-{i}-{j}-{k}-{m}")
                    for n in range(15):
                        l4.add_child(name=f"L5-{i}-{j}-{k}-{m}-{n}")

    l2_0_0 = SubgroupUnit.objects.get(name="L2-0-0")
    event = Event.objects.create(name="Evento Profundo")
    event.subgroup_unit.add(l2_0_0)

    return event


@timed
def get_units_with_access_to(event: Event):
    access_nodes = []
    for unit in event.subgroup_unit.all():
        access_nodes.extend(unit.get_descendants().select_related())
        access_nodes.append(unit)
    return access_nodes


def main():
    logger.info("🏗️ Criando árvore e evento...")
    event, creation_time = build_tree_and_event()
    logger.info(f"✅ Árvore criada e evento associado em {creation_time:.2f}s")

    logger.info("🔍 Medindo tempo para obter todos os nós com acesso ao evento...")
    units, access_time = get_units_with_access_to(event)
    logger.info(f"✅ {len(units)} unidades com acesso encontradas em {access_time:.6f}s")


if __name__ == "__main__":
    main()
