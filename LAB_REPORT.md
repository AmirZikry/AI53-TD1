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
    Engineering checkpoint 1: Why is a working model.pt insufficient evidence that an experiment is reproducible?
The model is already done and ready to be used but other users couldn't know the parameters used in order to train it.      
</summary>
</details>



<details>
    <summary>
    Engineering Checkpoint 2: Does random_state=42 guarantee bit-for-bit identical results on every CPU/GPU/software stack?
    No because each stack have different levels of precision, so there might be a minor numerical difference at the least significant bit. 
</summary>
</details>

<details>
    <summary>
    Engineering Checkpoint 3: 
    In one sentence each, state what the Git remote stores, what the DVC remote stores, and whether git push transfers the DVC-managed raw images>
    Git remote stores: source code, params.yaml,pyproject.toml, uv.lock and .dvc metadata pointers
    DVC remote stores: Large model artefacts,large generated files, DVC-managed dataset content
    Git push doesn't push the whole dataset in the repository, instead it pushes the metadata required to pull the dataset from dvc

</summary>
</details>

<details>
    <summary>
    4.2 
    1) Yes, validate runs first for quality check, if it fails, prepare will not run
    2) Yes, directly reads and processes the raw image files from data/raw
    3) data.image_size, all the items under train, augmentation, compute, tracking sections
    4) evaluate does not depend on the train stage directly; instead, it fetches a specific candidate model from MLflow using the Run ID stored in selection.run_id. Tracking selection.run_id in params: ensures DVC knows the current test outputs are stale and automatically reruns evaluate whenever you select a different MLflow Run ID
    5) reports/test_metrics.json

</summary>
</details>

<details>
    <summary>
Engineering Checkpoint 4
Git: Records the exact versioned source code, pipeline definitions (dvc.yaml), and configuration settings (params.yaml) used for the run
DVC: Records cryptographic hashes of the raw and processed datasets, stage dependencies, and output artifacts (dvc.lock) to track data lineage and verify pipeline reproducibility.
MLflow: Records per-run execution telemetry—including hyperparameters, dataset inputs, epoch-by-epoch metrics, training duration, provenance artifacts, and the serialized model binary with its signature—in an experiment tracking store.
</summary>
</details>

<details>
    <summary>
| Change | VALIDATE | PREPARE | TRAIN | EVALUATE |
| :--- | :--- | :--- | :--- | :--- |
| Change `train.learning_rate` | REUSED | REUSED | RERUN | REUSED |
| Change `data.image_size` | REUSED | RERUN | RERUN | NEEDS UPDATE |
| Edit `src/validate_data.py`; the quality report stays the same | RERUN | REUSED | REUSED | REUSED |
| Edit only `README.md` | REUSED | REUSED | REUSED | REUSED |

Change train.learning_rate
VALIDATE & PREPARE (REUSED): Neither stage lists train.learning_rate in its params: or deps:, so their inputs are unchanged.   
TRAIN (RERUN): Lists train.learning_rate under params:, so DVC detects a parameter change and reruns training.  
EVALUATE (REUSED): Does not depend on train or train.learning_rate, and selection.run_id remains fixed to the previously selected MLflow Run. 

Edit src/validate_data.py;
VALIDATE (RERUN): src/validate_data.py is in validate's deps:, so DVC reruns validate.   
PREPARE, TRAIN, EVALUATE (REUSED): Because reports/data_quality.json is deterministic and its content does not change after validate finishes, prepare's input dependency (reports/data_quality.json) is unchanged, so DVC skips all downstream stages.  

RUN A: 8fa943ff6c17a3c874d2b152e9d7980602a5cd50c0d8156625bd00590a3d8c6c
Running it again without changes skips every stage.
Running it after adding a comment reruns validate and reuse the else 

</summary>
</details>