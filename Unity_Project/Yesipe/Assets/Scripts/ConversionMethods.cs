using UnityEngine;

public static class ConversionMethods
{
    public static Vector2 PolarToCartesian(float angle, float radius)
    {
        float angleRad = (Mathf.PI / 180f) * (angle - 90f);
        float x = radius * Mathf.Cos(angleRad);
        float y = radius * Mathf.Sin(angleRad);
        return new Vector2(x, y);
    }

    //public static Vector2 CartesianToPolar(Vector2 position)
    //{
    //    float angle = Mathf.Acos(position.x / position.magnitude);
    //    float distance = Mathf.Sqrt(Mathf.Pow(position.x, 2) + Mathf.Pow(position.y, 2));
    //    return new Vector2(angle, distance);
    //}
}
