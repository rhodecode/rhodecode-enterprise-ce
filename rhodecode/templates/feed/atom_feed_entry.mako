## -*- coding: utf-8 -*-

${_('%(user)s commited on %(date)s UTC') % {
'user': h.person(commit.author),
'date': h.format_date(commit.date)
}}
<br/>
% if commit.branch:
    branch: ${commit.branch} <br/>
% endif

% for bookmark in getattr(commit, 'bookmarks', []):
    bookmark: ${bookmark} <br/>
% endfor

% for tag in commit.tags:
    tag: ${tag} <br/>
% endfor

commit: <a href="${h.url('changeset_home', repo_name=c.rhodecode_db_repo.repo_name, revision=commit.raw_id, qualified=True)}">${h.show_id(commit)}</a>
<pre>
${h.urlify_commit_message(commit.message)}

% for change in parsed_diff:
  % if limited_diff:
  ${_('Commit was too big and was cut off...')}
  % endif
  ${change['operation']} ${change['filename']} ${'(%(added)s lines added, %(removed)s lines removed)' % {'added': change['stats']['added'], 'removed': change['stats']['deleted']}}
% endfor

% if feed_include_diff:
${diff_processor.as_raw()}
% endif
</pre>
