#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from collections import defaultdict
import os

def parse_edges(lines):
    """各行 'u, v, w' を (u:int, v:int, w:float) に変換"""
    edges = []
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        parts = [p.strip() for p in s.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Invalid line (need 'u, v, w'): {raw!r}")
        u = int(parts[0]); v = int(parts[1]); w = float(parts[2])
        edges.append((u, v, w))
    return edges

def build_graph(edges, undirected=False):
    """エッジ集合から隣接リストを作成"""
    g = defaultdict(list)
    nodes = set()
    for u, v, w in edges:
        nodes.add(u); nodes.add(v)
        g[u].append((v, w))
        if undirected:
            g[v].append((u, w))
    # 長い辺から試すと枝刈りが効きやすい
    for u in g:
        g[u].sort(key=lambda x: x[1], reverse=True)
    return g, sorted(nodes)

def longest_simple_path(g, nodes):
    """DFSで同じ点を二度通らない最長経路を探索"""
    max_w = 0.0
    for u in g:
        if g[u]:
            max_w = max(max_w, g[u][0][1])

    best_len = -1.0
    best_path = []
    visited = set()

    def dfs(u, cur_len, path):
        nonlocal best_len, best_path
        # 粗い上界による枝刈り
        upper = cur_len + max_w * (len(nodes) - len(path))
        if upper <= best_len + 1e-12:
            return

        moved = False
        for v, w in g.get(u, []):
            if v in visited:
                continue
            visited.add(v)
            path.append(v)
            dfs(v, cur_len + w, path)
            path.pop()
            visited.remove(v)
            moved = True

        if not moved and cur_len > best_len + 1e-12:
            best_len = cur_len
            best_path = path[:]

    for s in nodes:
        visited.clear()
        visited.add(s)
        dfs(s, 0.0, [s])

    return best_len, best_path

def main():
    ap = argparse.ArgumentParser(description="Find the longest one-way ticket path")
    ap.add_argument("--undirected", action="store_true",
                    help="入力を無向として扱う（デフォルトは有向）")
    ap.add_argument("infile", nargs="?", help="入力ファイル（省略時は標準入力）")
    args = ap.parse_args()

    if args.infile and os.path.exists(args.infile):
        with open(args.infile, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()

    edges = parse_edges(lines)
    g, nodes = build_graph(edges, undirected=args.undirected)
    _, path = longest_simple_path(g, nodes)
    for v in path:
        print(v)

if __name__ == "__main__":
    main()