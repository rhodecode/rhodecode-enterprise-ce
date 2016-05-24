## -*- coding: utf-8 -*-
Auto status change to |under_review|

.. role:: added
.. role:: removed
.. parsed-literal::

  Changed commits:
    * :added:`${len(added_commits)} added`
    * :removed:`${len(removed_commits)} removed`

  %if not changed_files:
  No file changes found
  %else:
  Changed files:
    %for file_name in added_files:
    * `A ${file_name} <#${'a_' + h.FID('', file_name)}>`_
    %endfor
    %for file_name in modified_files:
    * `M ${file_name} <#${'a_' + h.FID('', file_name)}>`_
    %endfor
    %for file_name in removed_files:
    * R ${file_name}
    %endfor
  %endif

.. |under_review| replace:: *"${under_review_label}"*