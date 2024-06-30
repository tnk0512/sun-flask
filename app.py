from flask import Flask, jsonify, request, render_template
import json

app = Flask(__name__)

# データを読み込む関数
def load_data():
    with open('dataset/viruses.json') as f:
        data = json.load(f)
    return data

# ノードの値を事前処理する関数
def preprocess_data(node):
    if 'children' not in node or len(node['children']) == 0:
        node['value'] = 1  # 葉ノードの値を1に設定
    else:
        for child in node['children']:
            preprocess_data(child)
        node['value'] = sum(child['value'] for child in node['children'])  # 親ノードの値を子ノードの値の合計に設定

# ルートURLにアクセスしたときにindex.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')

# 初期データを提供するエンドポイント
@app.route('/data', methods=['GET'])
def get_data():
    data = load_data()
    preprocess_data(data)  # データを事前処理
    return jsonify(data)

# 新しいサブツリーを提供するエンドポイント
@app.route('/subtree', methods=['POST'])
def get_subtree():
    target_name = request.json['target_name']
    data = load_data()
    preprocess_data(data)  # データを事前処理

    def find_node(name, node):
        if node['name'] == name:
            return node
        if 'children' in node:
            for child in node['children']:
                result = find_node(name, child)
                if result:
                    return result
        return None
    
    def get_parent_node(name, node, parent=None):
        if node['name'] == name:
            return parent
        if 'children' in node:
            for child in node['children']:
                result = get_parent_node(name, child, node)
                if result:
                    return result
        return None

    def limit_depth(node, depth, max_depth):
        if depth >= max_depth:
            node.pop('children', None)
        else:
            if 'children' in node:
                for child in node['children']:
                    limit_depth(child, depth + 1, max_depth)

    subtree = find_node(target_name, data)
    if subtree:
        limit_depth(subtree, 0, 4)  # 深さを制限する
    parent = get_parent_node(target_name, data)
    
    return jsonify({'subtree': subtree, 'parent': parent})

if __name__ == '__main__':
    app.run(debug=True)
