# Asynchronous HTTP requests

## Sequence Diagrams

| Synchronous HTTP requests 🐢 | Asynchronous HTTP requests 🐇 |
| :------------------------ | :------------------------: |
| ![Sync HTTP Diagram](http://www.plantuml.com/plantuml/png/hP7HIyCm4CRVyrVSOorjeNqKaGs6Sw1XwDv4GbcFDPYacBiY--_jvh2P3owKlIMv--xttPSPSUsvjqQmPeFmkdVRrdUkwmaUDvirlE1dZyGaH54KaAPFcXYUaQZU8QmMbAOm5CJIrjeyQ6hHGtuFn-jylO9RC8D0sH-1qWqbXAv1h_3Gai47xhywtz3DsOYxF0zdl8rwLMO7O0R1atm_cLlYw6s1FEWl-zjXQ2y9IVzwEXvFC5LE0bJnW4fCtKB6GsGGuvovthOM7ST5MF_s9-UVDHOkPpf2LNaTNXNBgyJK7ULVfenbIZ53r_JMV0C0) | ![Async HTTP Diagram](http://www.plantuml.com/plantuml/png/lP9HIyCm58NVyolkurQsmVeuH5QOpe4hG_ecKa9pMODfWxctwlwzdLEJWTPImRUc-Sx9oJrP4al7JMK4QpO82HtgedIsjWt1JPRju0wV6YGc8MQp6KJHhIQ6BHB9FS9cHL44xOOGwqfgSwsfH0VJItXV9hiDBC2qYhmwANAjQ4HOAtGv7f49FEBXnJf5upEBY-aqzBZt-dm-EPuuWU1N-l0PRuq-tGgvDVWneLyk82iTIhMprbozOj6mTKB8WlMpP0p9hdlkCRpcA4my7YIBXydIhacUFhSVzBmt6VScKo4KVZyxNr72B8komfh_jHxvTUpe_47v3T_NtttYOJvfwFDxeubdvpsvk1_NqUKIQzLKvWq0) |

## Performance

The following table makes a performance comparison between making synchronous and asynchronous HTTP requests to Gmail
API.

| Use Case                  | Result Count  | Synchronous 🐢 | Asynchronous 🐇 |
| :-----------------------: | :-----------: | :------------: | :-------------: |
| `save_attachments`        | 27            | 16.460s        | 4.022s          |
| `uber_eats_stats`         | 207           | 53.938s        | 8.496s          |
| `uber_eats_save_expenses` | 207           | 52.034s        | 6.882s          |
