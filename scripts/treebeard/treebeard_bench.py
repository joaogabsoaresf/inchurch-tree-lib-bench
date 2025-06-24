import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from scripts.base import *
setup_django('config.settings')

from treebeard_tests.models import SubgroupUnit
logger = setup_logger('treebeard')


@timed
def build_large_tree():
    SubgroupUnit.objects.all().delete()
    root = SubgroupUnit.add_root(name="Root")

    def create_level(parent_nodes, count_per_parent, prefix):
        new_level = []
        for i, parent in enumerate(parent_nodes):
            for j in range(count_per_parent):
                # criar filho com parent.add_child
                node = parent.add_child(name=f"{prefix}-{i}-{j}")
                new_level.append(node)
        return new_level

    level_1 = create_level([root], 3, "L1")
    level_2 = create_level(level_1, 3, "L2")
    level_3 = create_level(level_2, 5, "L3")
    level_4 = create_level(level_3, 10, "L4")
    level_5 = create_level(level_4, 15, "L5")

    total_nodes = 1 + len(level_1) + len(level_2) + len(level_3) + len(level_4) + len(level_5)
    logger.info(f"Árvore construída: {total_nodes} nós no total.")
    return root


@timed
def create_node_at_depth(target_depth_name, parent_name):
    parent = SubgroupUnit.objects.filter(name=parent_name).first()
    if not parent:
        raise Exception(f"Parent '{parent_name}' not found")
    parent.add_child(name=f"NewNode_{target_depth_name}")


@timed
def query_ancestors(node_name):
    node = SubgroupUnit.objects.get(name=node_name)
    return list(node.get_ancestors())


@timed
def query_descendants(node_name):
    node = SubgroupUnit.objects.get(name=node_name)
    return list(node.get_descendants())


@timed
def move_node_to_new_parent(node_name, new_parent_name):
    node = SubgroupUnit.objects.get(name=node_name)
    new_parent = SubgroupUnit.objects.get(name=new_parent_name)
    node.move(new_parent, pos='sorted-child')  # posição válida para node_order_by
    node.save()


def main():
    logger.info("⏳ Construindo árvore com estrutura 3-3-5-10-15 usando treebeard...")
    _, duration = build_large_tree()
    logger.info(f"✅ Árvore construída em {duration:.2f}s")

    scenarios = [
        ("L1", "L1-0-0"),
        ("L2", "L2-0-0"),
        ("L3", "L3-0-0"),
        ("L4", "L4-0-0"),
        ("L5", "L5-0-0"),
    ]

    logger.info("\n📌 Medindo tempo de criação de novo nó em diferentes profundidades:")
    for label, parent_name in scenarios:
        _, duration = create_node_at_depth(label, parent_name)
        logger.info(f"+ Novo nó em {label} criado em {duration:.6f}s")

    logger.info("\n🔎 Medindo tempo de leitura de descendentes:")
    for label, node_name in scenarios:
        descendants, duration = query_descendants(node_name)
        logger.info(f"📂 Descendentes de {node_name}: {len(descendants)} nós em {duration:.6f}s")

    logger.info("\n🔍 Medindo tempo de leitura de ancestrais:")
    for label, node_name in reversed(scenarios):
        ancestors, duration = query_ancestors(node_name)
        logger.info(f"📁 Ancestrais de {node_name}: {len(ancestors)} níveis em {duration:.6f}s")

    logger.info("\n🔁 Movimentando um nó profundo:")
    _, duration = move_node_to_new_parent("L5-0-0", "L1-0-1")
    logger.info(f"🔄 Nó L5-0-0 movido para L1-0-1 em {duration:.6f}s")


if __name__ == "__main__":
    main()
