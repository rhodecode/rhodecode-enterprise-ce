<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">${_('Custom IP Whitelist')}</h3>
    </div>
    <div class="panel-body">
        <div class="ips_wrap">
  <table class="rctable ip-whitelist">
    <tr>
      <th>IP Address</th>
      <th>IP Range</th>
      <th>Description</th>
      <th></th>
    </tr>
    %if c.default_user_ip_map and c.inherit_default_ips:
        %for ip in c.default_user_ip_map:
          <tr>
            <td class="td-ip"><div class="ip">${ip.ip_addr}</div></td>
            <td class="td-iprange"><div class="ip">${h.ip_range(ip.ip_addr)}</div></td>
            <td class="td-description">${h.literal(_('Inherited from %s') % h.link_to('*default*',h.url('admin_permissions_ips')))}</td>
            <td></td>
          </tr>
        %endfor
    %endif

    %if c.user_ip_map:
        %for ip in c.user_ip_map:
          <tr>
            <td class="td-ip"><div class="ip">${ip.ip_addr}</div></td>
            <td class="td-iprange"><div class="ip">${h.ip_range(ip.ip_addr)}</div></td>
            <td class="td-description"><div class="ip">${ip.description}</div></td>
            <td class="td-action">
                ${h.secure_form(url('edit_user_ips', user_id=c.user.user_id),method='delete')}
                    ${h.hidden('del_ip_id',ip.ip_id)}
                    ${h.submit('remove_',_('Delete'),id="remove_ip_%s" % ip.ip_id,
                    class_="btn btn-link btn-danger", onclick="return confirm('"+_('Confirm to delete this ip: %s') % ip.ip_addr+"');")}
                ${h.end_form()}
            </td>
          </tr>
        %endfor
    %endif
    %if not c.default_user_ip_map and not c.user_ip_map:
        <tr>
          <td><h2 class="ip">${_('All IP addresses are allowed')}</h2></td>
          <td></td>
          <td></td>
          <td></td>
        </tr>
    %endif
  </table>
</div>

        <div>
    ${h.secure_form(url('edit_user_ips', user_id=c.user.user_id),method='put')}
    <div class="form">
        <!-- fields -->
        <div class="fields">
             <div class="field">
                <div class="label">
                    <label for="new_ip">${_('New IP Address')}:</label>
                </div>
                <div class="input">
                    ${h.text('new_ip')} ${h.text('description', placeholder=_('Description...'))}
                    <span class="help-block">${_('Enter comma separated list of ip addresses like 127.0.0.1,\n'
                     'or use a ip address with a mask 127.0.0.1/24, to create a network range.\n'
                     'To specify multiple address range use 127.0.0.1-127.0.0.10 syntax')}</span>
                </div>
             </div>
            <div class="buttons">
              ${h.submit('save',_('Add'),class_="btn btn-small")}
              ${h.reset('reset',_('Reset'),class_="btn btn-small")}
            </div>
        </div>
    </div>
    ${h.end_form()}
</div>
    </div>
</div>
