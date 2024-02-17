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

    for node in list(self.dynamic_definition.included_nodes):
      if not self.project.nodes[node].root_node:
        file_to_move = self.project.extensions['POP_NODE']._pop_node(
          node,
          from_project=source_project.title(),
          rewrite_buffer=False)
      else:
        file_to_move = self.project.nodes[node].filename
      self.project.project_list.move_file(
        file_to_move,
        source_project.title(),
        dest_project.title())

    return input_contents

urtext_directives = [MoveNodesToProject]