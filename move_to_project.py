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
    changed_ids = {} # map old to new (resolved) IDs 

    for node_id in list(self.dynamic_definition.included_nodes):
      node = self.project.nodes[node_id]
      nodes_as_nested.setdefault(node.nested, [])
      nodes_as_nested[node.nested].append(node_id)

    for nested_level in nodes_as_nested.keys():
      for node_id in nodes_as_nested[nested_level]:
        if node_id in moved_nodes:
          continue
        moved_nodes.append(node_id)
        moved_nodes.extend([n.id for n in node.descendants()]) #verified this works.
        if not self.project.nodes[node_id].root_node:
          file_to_move = self.project.extensions['POP_NODE']._pop_node(
            node_id,
            from_project=source_project.title(),
            leave_pointer=False)
        else:
          file_to_move = self.project.nodes[node_id].filename
        files_to_move.append(file_to_move)
    for file in files_to_move:
      file_changed_ids = self.project.project_list.move_file(
        file,
        source_project.title(),
        dest_project.title(),
        replace_links=False)
      if file_changed_ids:
        changed_ids.update(file_changed_ids)
    
    nodes_to_update = self._get_links_to_multiple(moved_nodes)
    
    #file update bug here
    for node_id in nodes_to_update: 
      for replacement_link in nodes_to_update[node_id]:
        if replacement_link in changed_ids:
          resolved_link = changed_ids[replacement_link]
        else:
          resolved_link = replacement_link
        self.project.nodes[node_id].replace_links(
          replacement_link,
          new_id=resolved_link,
          new_project=dest_project.title())

    return input_contents

  def _get_links_to_multiple(self, to_ids):
      """
      Give a list of target ids, returns a dict with the keys being
      ids of project nodes and the values being the target id(s) linked
      to by that node.
      """
      if not isinstance(to_ids, list):
          to_ids = [to_ids]
      links_to = {}

      for project_node in [n for n in self.dynamic_definition.project.nodes.values() if not n.dynamic]:
        for to_id in to_ids:
            if to_id in project_node.links_ids():
                links_to.setdefault(project_node.id,[])
                links_to[project_node.id].append(to_id)
      return links_to

urtext_directives = [MoveNodesToProject]