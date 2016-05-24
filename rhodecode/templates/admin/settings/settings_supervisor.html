%if c.connection_error:
    <h4>Cannot connect to supervisor: ${c.connection_error}</h4>
%else:
<table class="rctable supervisor">
    <tr>
        <th>Name</th>
        <th>Description</th>
        <th>State</th>
    </tr>

% for proc,vals in c.supervisor_procs.items():
    <tr>
    %if vals.get('_rhodecode_error'):
        <td>${proc}</td>
        <td>${vals['_rhodecode_error']}</td>
        <td></td>
    %else:
        <td class="td-componentname"><a href="${h.url('admin_settings_supervisor_log', procid=proc, offset=c.log_size)}">${vals['name']}</a></td>
        <td class="td-description">${vals['description']}</td>
        <td class="td-state">${vals['statename']}</td>
    %endif
    ##<td class="td-action"> start | stop | restart</td>
    </tr>

% endfor
</table>
%endif
