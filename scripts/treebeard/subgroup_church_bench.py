import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from treebeard_tests.models import SubgroupUnit, Church, Subgroup

logger = setup_logger('treebeard')


@timed
def build_tree_and_entities():
    # Limpa as tabelas
    Church.objects.all().delete()
    Subgroup.objects.all().delete()
    SubgroupUnit.objects.all().delete()

    root = SubgroupUnit.add_root(name="Root")
    subgroup = Subgroup.objects.create(name="Main Subgroup", subgroup_unit=root)

    last_level_nodes = []

    for i in range(3):
        l1 = root.add_child(name=f"{i}")
        for j in range(3):
            l2 = l1.add_child(name=f"{i}.{j}")
            for k in range(5):
                l3 = l2.add_child(name=f"{i}.{j}.{k}")
                for m in range(10):
                    l4 = l3.add_child(name=f"{i}.{j}.{k}.{m}")
                    for n in range(15):
                        l5 = l4.add_child(name=f"{i}.{j}.{k}.{m}.{n}")
                        last_level_nodes.append(l5)

    deep_node = last_level_nodes[-1]
    church = Church.objects.create(name="Deep Church", node=deep_node)

    return subgroup, church


@timed
def get_descendants(subgroup):
    # Com treebeard, pegue descendentes do nó associado ao subgroup
    return list(subgroup.subgroup_unit.get_descendants())


@timed
def get_church_position(church):
    # Posição completa: ancestrais + o próprio nó
    return list(church.node.get_ancestors())


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
