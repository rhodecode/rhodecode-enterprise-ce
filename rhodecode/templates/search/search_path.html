<table class="rctable search-results">
    <tr>
        <th>${_('Repository')}</th>
        <th>${_('File')}</th>
        ##TODO: add 'Last Change' and 'Author' here
    </tr>
    %for entry in c.formatted_results:
        ## search results are additionally filtered, and this check is just a safe gate
        % if h.HasRepoPermissionAny('repository.write','repository.read','repository.admin')(entry['repository'], 'search results path check'):
            <tr class="body">
                <td class="td-componentname">
                    %if h.get_repo_type_by_name(entry.get('repository')) == 'hg':
                        <i class="icon-hg"></i>
                    %elif h.get_repo_type_by_name(entry.get('repository')) == 'git':
                        <i class="icon-git"></i>
                    %elif h.get_repo_type_by_name(entry.get('repository')) == 'svn':
                        <i class="icon-svn"></i>
                    %endif
                    ${h.link_to(entry['repository'], h.url('summary_home',repo_name=entry['repository']))}
                </td>
                <td class="td-componentname">
                    ${h.link_to(h.literal(entry['f_path']),
                        h.url('files_home',repo_name=entry['repository'],revision='tip',f_path=entry['f_path']))}
                </td>
            </tr>
        % endif
    %endfor
</table>

%if c.cur_query and c.formatted_results:
<div class="pagination-wh pagination-left">
    ${c.formatted_results.pager('$link_previous ~2~ $link_next')}
</div>
%endif