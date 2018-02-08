import remi
import remi.gui as gui
import pymarkoff
import os
import random

resource_dir = os.path.join(os.path.dirname(__file__), 'res')
if not os.path.isdir(resource_dir):
    os.makedirs(resource_dir)
graph_img = os.path.join(resource_dir, 'markov_graph.png')
try:
    os.remove(graph_img)
except FileNotFoundError:
    pass


class MyApp(remi.App):
    def __init__(self, *args):
        # supply a path for finding files
        # https://github.com/dddomodossola/remi/issues/207
        super().__init__(*args, static_file_path=resource_dir)

    def generate_output(self, *args):
        m = pymarkoff.from_sentences('\n'.join([
            line.strip() for line in self.input_element.get_value().split('\n')
            if len(line) > 0
        ]))
        text = m.next_sentence(max_length=100)
        self.output_element.set_text(text)
        g = m.to_graph()
        num_nodes = len(m.transitions)
        num_edges = sum(len(x) for x in m.transitions.values())
        self.label3.set_text(f'{num_nodes} nodes, {num_edges} edges')
        target = '/' + graph_img + '?' + str(random.random())
        try:
            os.remove(graph_img)
        except FileNotFoundError:
            pass
        if num_nodes < 250 and num_edges < 250:
            g.write_png(graph_img)
        self.graph_img.attributes['src'] = target
        self.graph_img.redraw()
        print('target', target)

    def main(self):
        # ========== Instantiate UI Elements ==========
        self.root = gui.VBox(
            style={
                'text-align': 'center',
            }, width=1200, margin='auto')
        self.container = gui.VBox(width='100%')
        self.title = gui.Label('Markov Text Generator.')
        self.instructions = gui.Label(
            'Paste or type your text and click generate.')
        self.label1 = gui.Label('Input')
        self.input_area = gui.VBox(width='100%')
        self.input_element = gui.TextInput(
            single_line=False, height=300, width='80%')
        self.input_element.style['border'] = '1px solid black'
        # self.input_element.set_on_change_listener(self.generate_output)
        self.generate_button = gui.Button('Generate')
        self.generate_button.set_on_click_listener(self.generate_output)

        self.label2 = gui.Label('Output')
        self.label3 = gui.Label('')
        self.output_element = gui.TextInput(height=300, width='80%')
        self.output_element.style['border'] = '1px solid black'

        self.graph_img = gui.Image(
            '/' + graph_img, width='100%', height='100%')
        self.quit_button = gui.Button('Quit', color='red')
        self.quit_button.set_on_click_listener(quit)

        # ========== Place UI Elements ==========
        self.root.append(self.container)
        self.container.append(self.title)
        self.container.append(self.instructions)
        self.input_area.append(self.label1)
        self.input_area.append(self.input_element)
        self.container.append(self.input_area)
        self.container.append(self.generate_button)
        self.container.append(self.label2)
        self.container.append(self.label3)
        self.container.append(self.output_element)
        self.container.append(self.graph_img)
        self.container.append(self.quit_button)

        return self.root


def main():
    remi.start(MyApp, )


if __name__ == '__main__':
    main()
