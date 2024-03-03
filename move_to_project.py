import pprint

"""
Problems:
  - dynamic nodes may get orphaned from their definitions
  - for some reason files are not always being dropped from the source project
  - getting "not included in the current project." a lot, after file is
    moved to dest project.
"""
class MoveNodesToProject:

  phase = 400
  name = ['MOVE_TO_PROJECT']

  def dynamic_output(self, input_contents):

    dest_project = self.project.project_list.get_project_from_link(self.argument_string)
    source_project = self.project
    
    if not dest_project:
      return ''.join([
        input_contents,'\n',
        'The project "%s" is not available.' % self.project.project_list.get_project_title_from_link(self.argument_string)])

    moved_nodes = []
    nodes_as_nested = {}
    files_to_move = []
    leave_links = self.have_flags('-leave_links')
    changed_ids = {} # map old to new (resolved) IDs 

    for node_id in list(self.dynamic_definition.included_nodes):
      node = self.project.nodes[node_id]
      nodes_as_nested.setdefault(node.nested, [])
      nodes_as_nested[node.nested].append(node_id)

    # Pop out nodes that are not root level
    # gather a list of all files that must be moved

    for nested_level in sorted(nodes_as_nested.keys()):
      for node_id in nodes_as_nested[nested_level]:
        if node_id in moved_nodes:
          continue
        moved_nodes.append(node_id)
        moved_nodes.extend([n.id for n in node.descendants()]) #verified this works.
        if not self.project.nodes[node_id].root_node:
          file_to_move = self.project.extensions['POP_NODE']._pop_node(
            node_id,
            from_project=source_project.title(),
            leave_pointer=False,
            leave_link=leave_links)
        else:
          file_to_move = self.project.nodes[node_id].filename
        files_to_move.append(file_to_move)

    # move each file, tracking changed IDs once added to the new project
    for file in files_to_move:
      ids_in_new_project = self.project.project_list.move_file(
        file,
        source_project.title(),
        dest_project.title(),
        replace_links=False)
      if ids_in_new_project:
        changed_ids.update(ids_in_new_project) 
        # dict of changed ids received from _check_file_for_duplicates

    # update links in both project:
    # destination project:
    #   - ? replace the links with resolved ids if they have changed - but this should happen automatically?
    #   - add the source project to links that still link back to it (are not in the new project).

    for original_id in moved_nodes:
      dest_project_id = changed_ids[node_id] if node_id in changed_ids else original_id
      for link in dest_project.nodes[dest_project_id].links:
        if link.node_id in changed_ids and link.node_id != changed_ids[link.node_id]:
          if link.node_id not in dest_project.nodes:
            dest_project.nodes[dest_project_id].replace_links(
                link.node_id,
                new_id=link.node_id,
                new_project=self.project.title())
      
    source_proj_links_to_update = self._get_links_to_multiple(moved_nodes)
    for link_id in source_proj_links_to_update: 
      for node_with_link_to_update in source_proj_links_to_update[node_id]:
          if node_with_link_to_update in self.project.nodes:
            self.project.nodes[node_with_link_to_update].replace_links(
              link_id,
              new_id=link_id,
              new_project=dest_project.title())

    return str(len(moved_nodes)) + ' nodes moved to %s' % self.utils.make_project_link(dest_project.title())

  def _get_links_to_multiple(self, to_ids):
      """
      Give a list of ids in the current project, returns a dict
      keys : ids of project nodes
      values :  id(s) linked to by that node.
      """
      if not isinstance(to_ids, list):
          to_ids = [to_ids]
      links_to = {}
      for node_id in to_ids:
        links_to[node_id] = self.project.get_links_to(node_id, include_dynamic=False)
      return links_to

urtext_directives = [MoveNodesToProject]