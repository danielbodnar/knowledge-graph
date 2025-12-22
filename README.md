<img style="width:100%" alt="knowledge_graph_banner" src="https://raw.githubusercontent.com/learning-commons-org/.github/refs/heads/main/assets/kg_hero.png" />

<p align="center">
  <a href="https://docs.learningcommons.org/knowledge-graph/v1-3-0/getting-started/download-the-data/" target="_blank">Getting set up</a>
</p>


## **About Knowledge Graph**
Knowledge Graph is a structured dataset that connects state academic standards, curricula, and learning science data from domain experts.

Key use cases include:

* **Standards alignment**: Identify how your content supports specific academic standards and create content rooted in learner competencies across all key subjects  
* **Instructional planning**: Create dependencies, learning progressions, and content coverage, starting with math in the Common Core State Standards  
* **Compare state standards**: Adapt content aligned to one state standard to other states, initially in math across Common Core State Standards and 15+ additional states  
* **Curriculum alignment:** Align your content or create additional materials aligned to curriculum (private-beta access only \- details below on how to join)

For complete setup instructions and usage examples, see the [full docs](https://docs.learningcommons.org/knowledge-graph/).

## **Repository contents**

| Path | Description |
| :---- | :---- |
| [LICENSE](./LICENSE.md) | Open source license details |

##  **Quick Start**

The knowledge graph data is available for download in graph native JSONL format.

## Files

* `nodes.jsonl`: This file contains graph node records, defining each node by a unique identifier, labels, and a set of associated properties.
* `relationships.jsonl`: This file contains graph relationship records, describing how nodes are connected, including the relationship type, properties, and the source and target nodes.

## Download options

There are two options to download the files: direct links, or using curl commands.

### Direct links  

Click links to download files directly. Files will download to your browser's default location (typically `~/Downloads`).

- [nodes.jsonl](https://cdn.learningcommons.org/knowledge-graph/v1.3.0/exports/nodes.jsonl?ref=github)  
- [relationships.jsonl](https://cdn.learningcommons.org/knowledge-graph/v1.3.0/exports/relationships.jsonl?ref=github)  

### Using curl commands  

If you don't have `curl` installed, see [installation instructions](https://github.com/curl/curl).  

```bash
curl -L "https://cdn.learningcommons.org/knowledge-graph/v1.3.0/exports/nodes.jsonl?ref=gh_curl" -o nodes.jsonl
curl -L "https://cdn.learningcommons.org/knowledge-graph/v1.3.0/exports/relationships.jsonl?ref=gh_curl" -o relationships.jsonl
```

## Querying with jq

One option to query the JSONL files is using [jq](https://jqlang.github.io/jq/). Example to extract Common Core math standards:

```bash
jq -c 'select((.labels | contains(["StandardsFrameworkItem"])) and .properties.jurisdiction == "Multi-State" and .properties.academicSubject == "Mathematics")' nodes.jsonl > common_core_math_standards.jsonl
```

This filters for nodes with:
- Label: `StandardsFrameworkItem`
- Jurisdiction: `Multi-State` (Common Core)
- Academic Subject: `Mathematics`

## **Support & Feedback**

We want to hear from you. For questions or feedback, please [open an issue](https://github.com/learning-commons-org/knowledge-graph/issues) or reach out to us at support@learningcommons.org. 

## **Partner with us**

**Learn more about our Knowledge Graph or join our private beta to access:**

* Full curriculum-aligned datasets

* Early access to new features and APIs

* Personalized support from the Knowledge Graph team

Contact us [here](https://learningcommons.org/contact/?utm_source=github&utm_medium=kg&utm_campaign=privatebeta).

## **Reporting Security Issues**

If you believe you have found a security issue, please responsibly disclose by contacting us at [security@learningcommons.org](mailto:security@learningcommons.org).

## **Disclaimer**

The resources provided in this repository are made available "as-is", without warranties or guarantees of any kind. They may contain inaccuracies, limitations, or other constraints depending on the context of use. Use of these resources is subject to [our Terms of Use](https://learningcommons.org/terms-of-use/).

By accessing or using these resources, you acknowledge that:

* You are responsible for evaluating their suitability for your specific use case.  
* Learning Commons makes no representations about the accuracy, completeness, or fitness of these resources for any particular purpose.  
* Any use of the materials is at your own risk, and Learning Commons is not liable for any direct or indirect consequences that may result.

Please refer to each resource’s README, license, and associated docs for any additional limitations, attribution requirements, or guidance specific to that resource.
