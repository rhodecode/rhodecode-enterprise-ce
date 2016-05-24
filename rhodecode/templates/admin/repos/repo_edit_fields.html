<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">${_('Custom extra fields for this repository')}</h3>
    </div>
    <div class="panel-body">
        %if c.visual.repository_fields:
            %if c.repo_fields:
            <div class="emails_wrap">
              <table class="rctable edit_fields">
                <th>${_('Label')}</th>
                <th>${_('Key')}</th>
                <th>${_('Type')}</th>
                <th>${_('Action')}</th>

              %for field in c.repo_fields:
                <tr>
                    <td class="td-tags">${field.field_label}</td>
                    <td class="td-hash">${field.field_key}</td>
                    <td class="td-type">${field.field_type}</td>
                    <td class="td-action">
                      ${h.secure_form(url('delete_repo_fields', repo_name=c.repo_info.repo_name, field_id=field.repo_field_id),method='delete')}
                            ${h.hidden('del_repo_field',field.repo_field_id)}
                            <button class="btn btn-link btn-danger" type="submit"
                                    onclick="return confirm('${_('Confirm to delete this field: %s') % field.field_key}');">
                                ${_('Delete')}
                            </button>
                      ${h.end_form()}
                    </td>
                </tr>
              %endfor
              </table>
            </div>
            %endif
            ${h.secure_form(url('create_repo_fields', repo_name=c.repo_name),method='put')}
            <div class="form">
                <!-- fields -->
                <div class="fields">
                     <div class="field">
                        <div class="label">
                            <label for="new_field_key">${_('New Field Key')}:</label>
                        </div>
                        <div class="input">
                            ${h.text('new_field_key', class_='medium')}
                        </div>
                     </div>
                     <div class="field">
                        <div class="label">
                            <label for="new_field_label">${_('New Field Label')}:</label>
                        </div>
                        <div class="input">
                            ${h.text('new_field_label', class_='medium', placeholder=_('Enter short label'))}
                        </div>
                     </div>

                     <div class="field">
                        <div class="label">
                            <label for="new_field_desc">${_('New Field Description')}:</label>
                        </div>
                        <div class="input">
                            ${h.text('new_field_desc', class_='medium', placeholder=_('Enter a full description for the field'))}
                        </div>
                     </div>

                    <div class="buttons">
                      ${h.submit('save',_('Add'),class_="btn")}
                      ${h.reset('reset',_('Reset'),class_="btn")}
                    </div>
                </div>
            </div>
            ${h.end_form()}
        %else:
          <h2>
            ${_('Extra fields are disabled. You can enable them from the Admin/Settings/Visual page.')}
          </h2>
        %endif
    </div>
</div>


