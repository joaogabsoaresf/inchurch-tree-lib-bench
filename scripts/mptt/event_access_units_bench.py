import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from mptt_tests.models import SubgroupUnit, Event

logger = setup_logger('mptt')


@timed
def build_tree_and_event():
    SubgroupUnit.objects.all().delete()
    Event.objects.all().delete()

    root = SubgroupUnit.objects.create(name="Root")
    for i in range(3):
        l1 = SubgroupUnit.objects.create(name=f"L1-{i}", parent=root)
        for j in range(3):
            l2 = SubgroupUnit.objects.create(name=f"L2-{i}-{j}", parent=l1)
            for k in range(5):
                l3 = SubgroupUnit.objects.create(name=f"L3-{i}-{j}-{k}", parent=l2)
                for m in range(10):
                    l4 = SubgroupUnit.objects.create(name=f"L4-{i}-{j}-{k}-{m}", parent=l3)
                    for n in range(15):
                        SubgroupUnit.objects.create(name=f"L5-{i}-{j}-{k}-{m}-{n}", parent=l4)

    SubgroupUnit.objects.rebuild()

    l2_0_0 = SubgroupUnit.objects.get(name="L2-0-0")
    event = Event.objects.create(name="Evento Profundo")
    event.subgroup_unit.add(l2_0_0)

    return event


@timed
def get_units_with_access_to(event: Event):
    access_nodes = []
    for unit in event.subgroup_unit.all():
        access_nodes.extend(unit.get_descendants(include_self=True))
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
