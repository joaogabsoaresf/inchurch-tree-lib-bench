import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from mptt_tests.models import SubgroupUnit, Church, Subgroup

logger = setup_logger('mptt')


@timed
def build_tree_and_entities():
    # Limpa
    Church.objects.all().delete()
    Subgroup.objects.all().delete()
    SubgroupUnit.objects.all().delete()

    root = SubgroupUnit.objects.create(name="Root")
    subgroup = Subgroup.objects.create(name="Main Subgroup", subgroup_unit=root)

    last_level_nodes = []

    for i in range(3):
        l1 = SubgroupUnit.objects.create(name=f"{i}", parent=root)
        for j in range(3):
            l2 = SubgroupUnit.objects.create(name=f"{i}.{j}", parent=l1)
            for k in range(5):
                l3 = SubgroupUnit.objects.create(name=f"{i}.{j}.{k}", parent=l2)
                for m in range(10):
                    l4 = SubgroupUnit.objects.create(name=f"{i}.{j}.{k}.{m}", parent=l3)
                    for n in range(15):
                        l5 = SubgroupUnit.objects.create(name=f"{i}.{j}.{k}.{m}.{n}", parent=l4)
                        last_level_nodes.append(l5)

    SubgroupUnit.objects.rebuild()

    deep_node = last_level_nodes[-1]
    church = Church.objects.create(name="Deep Church", node=deep_node)

    return subgroup, church


@timed
def get_descendants(subgroup):
    return subgroup.get_all_descendants()


@timed
def get_church_position(church):
    return church.get_full_position()


def main():
    logger.info("🏗️ Iniciando criação da árvore e entidades...")
    (subgroup, church), duration = build_tree_and_entities()
    logger.info(f"✅ Árvore e entidades criadas em {duration:.2f}s")

    descendants, duration = get_descendants(subgroup)
    logger.info(f"📂 Descendentes de Subgroup: {len(descendants)} nós em {duration:.6f}s")

    position, duration = get_church_position(church)
    logger.info(f"📍 Posição completa da Church: {len(position)} níveis em {duration:.6f}s")


if __name__ == "__main__":
    main()
