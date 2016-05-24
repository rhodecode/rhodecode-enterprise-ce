<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">${_('Built in Mercurial hooks - read only')}</h3>
    </div>
    <div class="panel-body">
        <div class="form">
            <div class="fields">
              % for hook in c.hooks:
                <div class="field">
                    <div class="label label">
                        <label for="${hook.ui_key}">${hook.ui_key}</label>
                    </div>
                    <div class="input" >
                      ${h.text(hook.ui_key,hook.ui_value,size=59,readonly="readonly")}
                    </div>
                </div>
              % endfor
            </div>
            <span class="help-block">${_('Hooks can be used to trigger actions on certain events such as push / pull. They can trigger Python functions or external applications.')}</span>
        </div>
    </div>
</div>


<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">${_('Custom hooks')}</h3>
    </div>
    <div class="panel-body">
        % if c.visual.allow_custom_hooks_settings:
        ${h.secure_form(url('admin_settings_hooks'), method='post')}
        <div class="form">
            <div class="fields">

              % for hook in c.custom_hooks:
              <div class="field"  id="${'id%s' % hook.ui_id }">
                <div class="label label">
                    <label for="${hook.ui_key}">${hook.ui_key}</label>
                </div>
                <div class="input" >
                    ${h.hidden('hook_ui_key',hook.ui_key)}
                    ${h.hidden('hook_ui_value',hook.ui_value)}
                    ${h.text('hook_ui_value_new',hook.ui_value,size=59)}
                    <span class="btn btn-danger"
                    onclick="ajaxActionHook(${hook.ui_id},'${'id%s' % hook.ui_id }')">
                    ${_('Delete')}
                    </span>
                </div>
              </div>
              % endfor

              <div class="field customhooks">
                <div class="label">
                  <div class="input-wrapper">
                     ${h.text('new_hook_ui_key',size=30)}
                  </div>
                </div>
                <div class="input">
                    ${h.text('new_hook_ui_value',size=59)}
                </div>
              </div>
              <div class="buttons">
                 ${h.submit('save',_('Save'),class_="btn")}
              </div>
            </div>
        </div>
        ${h.end_form()}
        %else:
            DISABLED
        % endif
    </div>
</div>


<script type="text/javascript">
function ajaxActionHook(hook_id,field_id) {
    var sUrl = "${h.url('admin_settings_hooks')}";
    var callback =  function (o) {
            var elem = $("#"+field_id);
            elem.remove();
        };
    var postData = {
      '_method': 'delete',
      'hook_id': hook_id,
      'csrf_token': CSRF_TOKEN
    };
    var request = $.post(sUrl, postData)
            .done(callback)
            .fail(function (data, textStatus, errorThrown) {
                alert("Error while deleting hooks.\nError code {0} ({1}). URL: {2}".format(data.status,data.statusText,$(this)[0].url));
        });
};
</script>
