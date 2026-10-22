# Public workspace safety policy

This is a **public** repository. Publish only manually reviewed, independently developed demonstration code, synthetic tests and sanitized documentation.

Do not commit original or modified ECU FLASH or EEPROM, private calibration tables, vehicle identifiers, immobilizer data, diagnostic exports, account credentials, signing keys, proprietary firmware, or copied commercial tools. Do not include them in Issues, Pull Requests, logs or artifacts either.

The publication guard checks file allowlists, basic content markers, text format and size. It cannot prove absence of confidential material. Manually inspect every change before publishing. Deleting an exposed secret in a subsequent commit does not remove it from Git history.
