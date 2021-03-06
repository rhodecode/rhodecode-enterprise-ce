Repository Functions
--------------------

Creating a |repo|
^^^^^^^^^^^^^^^^^

To create a |repo| in |RCE|, use the following steps.
  
1. From the |RCE| interface, select :menuselection:`Admin --> Repositories`
2. From the |repo| page, select :guilabel:`Add Repository`
3. On the :guilabel:`Add Repository` page, complete the following |repo|
   details:
  
   * :guilabel:`Name`
   * :guilabel:`Description`
   * :guilabel:`Set the repository group`
   * :guilabel:`Set the repository type`
   * :guilabel:`Specify if it is a public or private repository`
4. Select :guilabel:`Save`

Importing a |repo|
^^^^^^^^^^^^^^^^^^

To import a |repo| in |RCE|, use the following steps.

1. From the |RCE| interface, select :menuselection:`Admin --> Repositories`
2. From the |repo| page, select :guilabel:`Add Repository`
3. On the :guilabel:`Add Repository` page, select
   :guilabel:`Import existing repository`
4. In the  :guilabel:`clone from` input field, specify the URL to the
   repository you want to import.
5. Complete the following repository details:

   * Name
   * Description
   * Set the |repo| group
   * Set the |repo| type
   * Specify if it is a public or private |repo|

6. Select :guilabel:`Add`

  .. note::

    | Make sure your |RCE| server can access the external |repo|.
    | Depending on the size of the repository the clone process may take a bit.


Cloning |repos|
^^^^^^^^^^^^^^^

To clone a |repo| in |RCE|, use the following steps.

1. From the |RCE| interface, select :menuselection:`Admin --> Repositories`
   and choose the |repo| you wish to clone.
2. Use the link in the :guilabel:`Clone URL` field to clone the |repo|
3. To clone, open a terminal on you computer and use one of the following
   examples

For |git|, use ``git clone URL``
For |hg|, use ``hg clone URL``
