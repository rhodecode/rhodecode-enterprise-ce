# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/

"""
Modified mercurial DAG graph functions that re-uses VCS structure

It allows to have a shared codebase for DAG generation for hg and git repos
"""

nullrev = -1


def grandparent(parent_idx_func, lowest_idx, roots, head):
    """
    Return all ancestors of head in roots which commit is
    greater or equal to lowest_idx.
    """
    pending = set([head])
    seen = set()
    kept = set()
    llowestrev = max(nullrev, lowest_idx)
    while pending:
        r = pending.pop()
        if r >= llowestrev and r not in seen:
            if r in roots:
                kept.add(r)
            else:
                pending.update(parent_idx_func(r))
            seen.add(r)
    return sorted(kept)


def _dagwalker(repo, commits):
    if not commits:
        return

    # TODO: johbo: Use some sort of vcs api here
    if repo.alias == 'hg':
        def get_parent_indexes(idx):
            return repo._remote.ctx_parents(idx)

    elif repo.alias in ['git', 'svn']:
        def get_parent_indexes(idx):
            return [commit.idx for commit in repo[idx].parents]

    indexes = [commit.idx for commit in commits]
    lowest_idx = min(indexes)
    known_indexes = set(indexes)

    gpcache = {}
    for commit in commits:
        parents = sorted(set([p.idx for p in commit.parents
                              if p.idx in known_indexes]))
        mpars = [p.idx for p in commit.parents if
                 p.idx != nullrev and p.idx not in parents]
        for mpar in mpars:
            gp = gpcache.get(mpar)
            if gp is None:
                gp = gpcache[mpar] = grandparent(
                    get_parent_indexes, lowest_idx, indexes, mpar)
            if not gp:
                parents.append(mpar)
            else:
                parents.extend(g for g in gp if g not in parents)

        yield (commit.idx, parents)


def _colored(dag):
    """annotates a DAG with colored edge information

    For each DAG node this function emits tuples::

      ((col, color), [(col, nextcol, color)])

    with the following new elements:

      - Tuple (col, color) with column and color index for the current node
      - A list of tuples indicating the edges between the current node and its
        parents.
    """
    seen = []
    colors = {}
    newcolor = 1

    for commit_idx, parents in dag:

        # Compute seen and next_
        if commit_idx not in seen:
            seen.append(commit_idx)  # new head
            colors[commit_idx] = newcolor
            newcolor += 1

        col = seen.index(commit_idx)
        color = colors.pop(commit_idx)
        next_ = seen[:]

        # Add parents to next_
        addparents = [p for p in parents if p not in next_]
        next_[col:col + 1] = addparents

        # Set colors for the parents
        for i, p in enumerate(addparents):
            if i == 0:
                colors[p] = color
            else:
                colors[p] = newcolor
                newcolor += 1

        # Add edges to the graph
        edges = []
        for ecol, eid in enumerate(seen):
            if eid in next_:
                edges.append((ecol, next_.index(eid), colors[eid]))
            elif eid == commit_idx:
                total_parents = len(parents)
                edges.extend([
                    (ecol, next_.index(p),
                     _get_edge_color(p, total_parents, color, colors))
                    for p in parents])

        # Yield and move on
        yield ((col, color), edges)
        seen = next_


def _get_edge_color(parent, total_parents, color, colors):
    if total_parents <= 1:
        return color

    return colors.get(parent, color)
