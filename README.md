# Readme for the Flask Implementation of the GFF3 Validator - SP21

Flask/Docker Implementation of GFF3 Validator

## Steps to Run Validator

1. Download/Pull Docker Container

    ```bash
    docker pull mmorro14/gff3-validator:latest
    ```

2. Run Docker Container

    ```bash
    docker run --publish 5000:5000 mmorro14/gff3-validator
    ```

3. Open localhost:5000 in the browser to use the validator

## Notes about the Validator

- Need internet connection to download the latest SO and GO Terms. Local use is not setup so an error will occur if the downloads fail
- Error handling is not defined therefore errors within the program itself will take the user to a try again page without specifying the error that occurred.
- [Docker Hub - mmorro14](https://hub.docker.com/r/mmorro14/gff3-validator)
- [GitHub - mmjh2021 - gff3-validator-flask repository](https://github.com/mmjh2021/gff3-validator-sp21-final-flask)

