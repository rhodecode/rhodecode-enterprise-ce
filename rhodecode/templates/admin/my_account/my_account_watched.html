<div class="panel panel-default">
  <div class="panel-heading">
    <h3 class="panel-title">${_('Your Watched Repositories')}</h3>
  </div>

  <div class="panel-body">
    <input class="q_filter_box" id="q_filter" size="15" type="text" name="filter" placeholder="${_('quick filter...')}" value=""/>

    <div id="repos_list_wrap">
        <table id="repo_list_table" class="display"></table>
    </div>
  </div>
</div>

<script>
$(document).ready(function() {

    var get_datatable_count = function(){
      var api = $('#repo_list_table').dataTable().api();
      $('#repo_count').text(api.page.info().recordsDisplay);
    };

    // repo list
    $('#repo_list_table').DataTable({
      data: ${c.data|n},
      dom: 'rtp',
      pageLength: ${c.visual.admin_grid_items},
      order: [[ 0, "asc" ]],
      columns: [
         { data: {"_": "name",
                  "sort": "name_raw"}, title: "${_('Name')}", className: "td-componentname" },
         { data: 'menu', className: "quick_repo_menu" },
         { data: {"_": "last_changeset",
                  "sort": "last_changeset_raw",
                  "type": Number}, title: "${_('Commit')}", className: "td-hash" }
      ],
      language: {
          paginate: DEFAULT_GRID_PAGINATION,
          emptyTable: _gettext("No repositories available yet.")
      },
      "initComplete": function( settings, json ) {
          get_datatable_count();
          quick_repo_menu();
      }
    });

    // update the counter when doing search
    $('#repo_list_table').on( 'search.dt', function (e,settings) {
      get_datatable_count();
    });

    // filter, filter both grids
    $('#q_filter').on( 'keyup', function () {
      var repo_api = $('#repo_list_table').dataTable().api();
      repo_api
        .columns(0)
        .search(this.value)
        .draw();
    });

    // refilter table if page load via back button
    $("#q_filter").trigger('keyup');

  });

</script>
