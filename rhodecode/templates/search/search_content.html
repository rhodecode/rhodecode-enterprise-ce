<%def name="highlight_text_file(terms, text, url, line_context=3,
                                max_lines=10,
                                mimetype=None, filepath=None)">
<%
lines = text.split('\n')
lines_of_interest = set()
matching_lines = h.get_matching_line_offsets(lines, terms)
shown_matching_lines = 0

for line_number in matching_lines:
    if len(lines_of_interest) < max_lines:
        lines_of_interest |= set(range(
            max(line_number - line_context, 0),
            min(line_number + line_context, len(lines) + 1)))
        shown_matching_lines += 1

%>
${h.code_highlight(
    text,
    h.get_lexer_safe(
        mimetype=mimetype,
        filepath=filepath,
    ),
    h.SearchContentCodeHtmlFormatter(
        linenos=True,
        cssclass="code-highlight",
        url=url,
        query_terms=terms,
        only_line_numbers=lines_of_interest
))|n}
%if len(matching_lines) > shown_matching_lines:
<a href="${url}">
  ${len(matching_lines) - shown_matching_lines} ${_('more matches in this file')}
</p>
%endif
</%def>

<div class="search-results">
%for entry in c.formatted_results:
  ## search results are additionally filtered, and this check is just a safe gate
  % if h.HasRepoPermissionAny('repository.write','repository.read','repository.admin')(entry['repository'], 'search results content check'):
      <div id="codeblock" class="codeblock">
        <div class="codeblock-header">
          <h2>
            %if h.get_repo_type_by_name(entry.get('repository')) == 'hg':
                <i class="icon-hg"></i>
            %elif h.get_repo_type_by_name(entry.get('repository')) == 'git':
                <i class="icon-git"></i>
            %elif h.get_repo_type_by_name(entry.get('repository')) == 'svn':
                <i class="icon-svn"></i>
            %endif
            ${h.link_to(entry['repository'], h.url('summary_home',repo_name=entry['repository']))}
          </h2>
          <div class="stats">
            ${h.link_to(h.literal(entry['f_path']), h.url('files_home',repo_name=entry['repository'],revision=entry.get('commit_id', 'tip'),f_path=entry['f_path']))}
            %if entry.get('lines'):
              | ${entry.get('lines', 0.)} ${ungettext('line', 'lines', entry.get('lines', 0.))}
            %endif
            %if entry.get('size'):
              | ${h.format_byte_size_binary(entry['size'])}
            %endif
            %if entry.get('mimetype'):
              | ${entry.get('mimetype', "unknown mimetype")}
            %endif
          </div>
          <div class="buttons">
            <a id="file_history_overview_full" href="${h.url('changelog_file_home',repo_name=entry.get('repository',''),revision=entry.get('commit_id', 'tip'),f_path=entry.get('f_path',''))}">
               ${_('Show Full History')}
            </a> |
              ${h.link_to(_('Annotation'), h.url('files_annotate_home', repo_name=entry.get('repository',''),revision=entry.get('commit_id', 'tip'),f_path=entry.get('f_path','')))}
             | ${h.link_to(_('Raw'), h.url('files_raw_home', repo_name=entry.get('repository',''),revision=entry.get('commit_id', 'tip'),f_path=entry.get('f_path','')))}
             | <a href="${h.url('files_rawfile_home',repo_name=entry.get('repository',''),revision=entry.get('commit_id', 'tip'),f_path=entry.get('f_path',''))}">
                ${_('Download')}
               </a>
          </div>
        </div>
        <div class="code-body search-code-body">
            ${highlight_text_file(c.cur_query, entry['content'],
            url=h.url('files_home',repo_name=entry['repository'],revision=entry.get('commit_id', 'tip'),f_path=entry['f_path']),
            mimetype=entry.get('mimetype'), filepath=entry.get('path'))}
        </div>
      </div>
    % endif
%endfor
</div>
%if c.cur_query and c.formatted_results:
<div class="pagination-wh pagination-left" >
    ${c.formatted_results.pager('$link_previous ~2~ $link_next')}
</div>
%endif

%if c.cur_query:
<script type="text/javascript">
$(function(){
  $(".code").mark(
    '${' '.join(h.normalize_text_for_matching(c.cur_query).split())}',
    {"className": 'match',
  });
})
</script>
%endif