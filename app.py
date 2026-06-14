from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pyArango.connection import Connection

app = Flask(__name__)
CORS(app)

# 连接 ArangoDB
conn = Connection(arangoURL='http://127.0.0.1:8529', username='root', password='12345')
db = conn['hotpot_multihop']


@app.route('/')
def index():
    return render_template('index.html')


# ========== API 1: 搜索问题 ==========
@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)

    query = """
        FOR q IN questions
            FILTER CONTAINS(LOWER(q.question), LOWER(@keyword))
            LIMIT @limit
            RETURN {
                id: q._key,
                question: q.question,
                answer: q.answer,
                type: q.type,
                level: q.level
            }
    """
    result = db.AQLQuery(query, bindVars={'keyword': keyword, 'limit': limit}, rawResults=True)
    return jsonify(list(result))


# ========== API 2: 随机示例 ==========
@app.route('/api/examples', methods=['GET'])
def examples():
    query = """
        FOR q IN questions
            SORT RAND()
            LIMIT 5
            RETURN {
                id: q._key,
                question: q.question,
                answer: q.answer,
                type: q.type
            }
    """
    result = db.AQLQuery(query, rawResults=True)
    return jsonify(list(result))


# ========== API 3: 多跳推理链 ==========
@app.route('/api/chain', methods=['GET'])
def chain():
    q_id = request.args.get('id', '')

    query = """
        LET q = DOCUMENT(CONCAT('questions/', @q_id))
        LET docs = (
            FOR v, e IN 1..1 OUTBOUND q supports
                SORT e.sentence_idx
                RETURN {
                    doc_key: v._key,
                    title: v.title,
                    sentence_idx: v.sentence_idx,
                    sentence_text: v.sentence_text
                }
        )
        LET path = (
            FOR v, e, p IN 1..5 OUTBOUND q supports, follows
                FILTER LENGTH(p.edges) >= 1
                LIMIT 20
                RETURN {
                    from: p.vertices[0]._key,
                    to: v._key,
                    hop: LENGTH(p.edges),
                    q_id: e.q_id
                }
        )
        RETURN {
            question: q.question,
            answer: q.answer,
            type: q.type,
            level: q.level,
            documents: docs,
            hop_path: path
        }
    """
    result = db.AQLQuery(query, bindVars={'q_id': q_id}, rawResults=True)
    data = list(result)
    return jsonify(data[0] if data else {})


# ========== API 4: 文档聚类（按引用热度） ==========
@app.route('/api/cluster', methods=['GET'])
def cluster():
    query = """
        FOR d IN documents
            LET ref_count = LENGTH(
                FOR v IN 1..1 INBOUND d supports
                    RETURN 1
            )
            COLLECT bucket = FLOOR(ref_count / 5) INTO group = d
            SORT bucket
            RETURN {
                bucket: bucket,
                count: LENGTH(group),
                min_refs: bucket * 5,
                max_refs: (bucket + 1) * 5,
                sample_docs: SLICE(group[*]._key, 0, 5)
            }
    """
    result = db.AQLQuery(query, rawResults=True)
    return jsonify(list(result))


# ========== API 5: 统计信息 ==========
@app.route('/api/stats', methods=['GET'])
def stats():
    query = """
        RETURN {
            questions: LENGTH(FOR q IN questions RETURN 1),
            documents: LENGTH(FOR d IN documents RETURN 1),
            supports: LENGTH(FOR e IN supports RETURN 1),
            follows: LENGTH(FOR e IN follows RETURN 1)
        }
    """
    result = db.AQLQuery(query, rawResults=True)
    return jsonify(list(result)[0])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)