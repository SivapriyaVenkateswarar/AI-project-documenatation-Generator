from tree_sitter_languages import get_parser

parser = get_parser("ruby")
code = """
class Hello
  def greet
    puts 'Hello'
  end
end
"""
tree = parser.parse(code.encode())
print(tree.root_node.sexp())
