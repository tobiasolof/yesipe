using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

[ExecuteAlways]
public class BlobShaderHelper : MonoBehaviour, IDragHandler
{
    //public Material material;
    public bool compensateForScreenSize;
    public float size = 1f;
    public List<BlobShaderHelper> colliders = new List<BlobShaderHelper>();
    Rigidbody2D rb;
    Material tempMaterial;

    public Color color;

    SpriteRenderer sprite;

    private void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        sprite = GetComponent<SpriteRenderer>();

        CreateAndAssignMaterial();
    }

    void CreateAndAssignMaterial()
    {
        tempMaterial = new Material(Shader.Find("Shader Graphs/Blob Shader 2D"));
        tempMaterial.SetVector("_Color", color);
        sprite.material = tempMaterial;
    }

    void Update()
    {
        if (!tempMaterial)
            CreateAndAssignMaterial();

        tempMaterial.SetVector("Vector4_3D31F990", new Vector4(size, size, size, size));
        tempMaterial.SetVector("_OwnSize", new Vector4(size, size, size, size));

        Vector3 newPos = compensateForScreenSize ? CompensateForScreenSize(transform.position) : transform.position;
        tempMaterial.SetVector("ObjectPosition", newPos);

        colliders = new List<BlobShaderHelper>();
        foreach (var item in Physics2D.OverlapCircleAll(transform.position, 5f))
        {
            if (item.gameObject != gameObject)
            {
                colliders.Add(item.GetComponent<BlobShaderHelper>());
            }
        }

        for (int i = 0; i < colliders.Count; i++)
        {
            Vector4 input = compensateForScreenSize ? CompensateForScreenSize(colliders[i].transform.position) : colliders[i].transform.position;
            input.w = colliders[i].size * Mathf.Pow(colliders[i].transform.localScale.x, 2);
            tempMaterial.SetVector($"Collider{i + 1}", input);
        }


    }

    Vector3 CompensateForScreenSize(Vector3 input)
    {
        return input - new Vector3(Screen.width / 2, Screen.height / 2);
    }

    public void OnMouseDrag()
    {
        
    }

    public void OnDrag(PointerEventData eventData)
    {
        rb.MovePosition(eventData.pointerCurrentRaycast.worldPosition);
    }
}
