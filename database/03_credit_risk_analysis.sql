WITH customer_exposure AS (
    SELECT
        customer_id,
        SUM(ead) AS total_exposure
    FROM loans
    GROUP BY customer_id
),

ranked_customers AS (
    SELECT
        customer_id,
        total_exposure,
        ROW_NUMBER() OVER (
            ORDER BY total_exposure DESC
        ) AS exposure_rank
    FROM customer_exposure
),

portfolio AS (
    SELECT
        SUM(ead) AS portfolio_exposure
    FROM loans
)

SELECT
    r.exposure_rank,
    r.customer_id,
    r.total_exposure,

    r.total_exposure / p.portfolio_exposure
        AS portfolio_share,

    SUM(r.total_exposure) OVER (
        ORDER BY r.exposure_rank
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) / p.portfolio_exposure
        AS cumulative_portfolio_share

FROM ranked_customers r
CROSS JOIN portfolio p
WHERE r.exposure_rank <= 20
ORDER BY r.exposure_rank;