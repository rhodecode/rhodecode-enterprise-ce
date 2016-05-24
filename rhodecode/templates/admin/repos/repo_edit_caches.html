<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">${_('Invalidate Cache for Repository')}</h3>
    </div>
    <div class="panel-body">
        ${h.secure_form(url('edit_repo_caches', repo_name=c.repo_name), method='put')}
        <div>
           <div class="fields">
              <p>
                 ${h.submit('reset_cache_%s' % c.repo_info.repo_name,_('Invalidate repository cache'),class_="btn btn-small",onclick="return confirm('"+_('Confirm to invalidate repository cache')+"');")}
              </p>
              <div class="field" >
                  <span class="help-block">
                  ${_('Manually invalidate the repository cache. On the next access a repository cache will be recreated.')}
                  </span>
              </div>

           </div>
        </div>
        ${h.end_form()}
    </div>
</div>


<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">
            ${(ungettext('List of repository caches (%(count)s entry)', 'List of repository caches (%(count)s entries)' ,len(c.repo_info.cache_keys)) % {'count': len(c.repo_info.cache_keys)})}
        </h3>
    </div>
    <div class="panel-body">
      <div class="field" >
           <table class="rctable edit_cache">
           <tr>
            <th>${_('Prefix')}</th>
            <th>${_('Key')}</th>
            <th>${_('Active')}</th>
            </tr>
          %for cache in c.repo_info.cache_keys:
              <tr>
                <td class="td-prefix">${cache.get_prefix() or '-'}</td>
                <td class="td-cachekey">${cache.cache_key}</td>
                <td class="td-active">${h.bool2icon(cache.cache_active)}</td>
              </tr>
          %endfor
          </table>
      </div>
    </div>
</div>


