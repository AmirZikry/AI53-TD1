<details>
    <summary>
    params.yaml
    To reproduce a test using the exact same parameters used before for reproducibility
    </summary>
</details>

<details>
    <summary>
    pyproject.toml
    Make sure the users have the same versions of dependencies before running the project
    </summary>
</details>

<details>
    <summary>
        uv-lock
        All environments consume the same locked resolution, making the Python software stack reproducible across compatible environments    
    </summary>
</details>

<details>
    <summary>
        .venv
        Local virtual environment that keeps a project's packages and dependencies separate from the global Python installation  
    </summary>
</details>

<details>
    <summary>
    Reproducibility
    Missing seed generator which prevents the model from generating a repeatable result as before. Making it hard for testing multiple times.
    </summary>
</details>
<details>
    <summary>
    Provenance and Train
Training runs lack provenance manifests (Git SHA, dirty flag, package versions, data identity) and MLflow experiment/model logging | Capture environment/Git/data metadata in `reports/run_manifest.json` and log parameters, datasets, metrics, artifacts, and the model to MLflow
    </summary>
</details>
<details>
    <summary>
    Validate_data
    Missing pre-training data quality gate; corrupted images, wrong split counts, or missing classes are not caught before training
    </summary>
</details>

<details>
    <summary>
    data
Transform data according to the needed shape before training. Avoiding missing data or unnormalized data in loaders     
</summary>
</details>

<details>
    <summary>
    Engineering Checkpoint 2: Does random_state=42 guarantee bit-for-bit identical results on every CPU/GPU/software stack?
    No because each stack have different levels of precision, so there might be a minor numerical difference at the least significant bit. 
</summary>
</details>